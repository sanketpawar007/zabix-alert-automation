"""
Ollama AI Provider
Uses locally-hosted Ollama for AI analysis (free, no API key required)
"""
import logging
import requests
from typing import Dict, Any
from .base import BaseAIProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseAIProvider):
    """Ollama AI provider for local LLM analysis"""

    def validate_config(self) -> None:
        """Validate Ollama configuration"""
        required_fields = ['ollama_base_url', 'ollama_model']
        missing = [f for f in required_fields if not self.config.get(f)]

        if missing:
            raise ValueError(f"Missing Ollama configuration: {', '.join(missing)}")

        # Set defaults
        self.base_url = self.config['ollama_base_url'].rstrip('/')
        self.model = self.config['ollama_model']
        self.timeout = self.config.get('ollama_timeout', 60)
        self.temperature = self.config.get('ollama_temperature', 0.7)
        self.max_tokens = self.config.get('ollama_max_tokens', 400)

    def analyze_alert(self, alert: Dict[str, Any]) -> str:
        """
        Analyze alert using Ollama LLM

        Args:
            alert: Alert dictionary

        Returns:
            AI analysis string
        """
        try:
            prompt = self._build_analysis_prompt(alert)

            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                },
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            analysis = result.get('response', '').strip()

            if not analysis:
                logger.warning("Ollama returned empty response")
                return self._get_fallback_analysis(alert)

            logger.info(f"Ollama analysis received for {alert.get('host', 'Unknown')}")
            return analysis

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            return self._get_fallback_analysis(alert)
        except Exception as e:
            logger.error(f"Unexpected error during Ollama analysis: {e}")
            return self._get_fallback_analysis(alert)

    def _build_analysis_prompt(self, alert: Dict[str, Any]) -> str:
        """Build the analysis prompt for Ollama"""
        return f"""You are a senior Juniper network engineer and reliability expert.
Analyze this Zabbix alert from a Juniper network device and provide a concise response.

ALERT DETAILS:
- Device:    {alert.get('host', 'Unknown')}
- Device IP: {alert.get('hostip', 'Unknown')}
- Problem:   {alert.get('name', 'Unknown')}
- Severity:  {alert.get('severity', 'Unknown')}
- Status:    {alert.get('status', 'Unknown')}
- Value:     {alert.get('value', 'N/A')}
- Trigger:   {alert.get('trigger', 'N/A')}
- Time:      {alert.get('time', 'N/A')}

Provide analysis in this EXACT format (max 5 lines total):
DIAGNOSIS: [What is happening and why]
IMPACT: [What services/users are affected]
ACTION 1: [Most important immediate step]
ACTION 2: [Second step if needed]
ROOT CAUSE: [Most likely cause]

Keep each line under 100 characters. Be specific and technical."""

    def _get_fallback_analysis(self, alert: Dict[str, Any]) -> str:
        """Provide basic analysis when AI is unavailable"""
        severity = alert.get('severity', 'Unknown')
        problem = alert.get('name', 'Unknown')
        status = alert.get('status', 'Unknown')

        if status == 'RESOLVED':
            return f"""DIAGNOSIS: Issue has been resolved
IMPACT: Service restored to normal operation
ACTION 1: Monitor for recurrence over next 30 minutes
ACTION 2: Review logs to identify root cause
ROOT CAUSE: Investigation required - AI analysis unavailable"""
        else:
            return f"""DIAGNOSIS: {severity} severity alert - {problem}
IMPACT: Potential service degradation - requires investigation
ACTION 1: Check device status and connectivity immediately
ACTION 2: Review recent changes and logs
ROOT CAUSE: Investigation required - AI analysis unavailable"""

    def health_check(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()

            # Check if our model is available
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]

            if self.model not in model_names:
                logger.warning(f"Model '{self.model}' not found in Ollama. Available: {model_names}")
                return False

            logger.info(f"Ollama health check passed - model '{self.model}' available")
            return True

        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
