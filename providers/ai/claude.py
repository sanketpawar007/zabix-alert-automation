"""
Claude AI Provider (Anthropic)
Production-grade AI provider using Claude API
"""
import logging
from typing import Dict, Any
from .base import BaseAIProvider

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseAIProvider):
    """Claude (Anthropic) AI provider for production use"""

    def validate_config(self) -> None:
        """Validate Claude configuration"""
        if not self.config.get('anthropic_api_key'):
            raise ValueError("Missing Anthropic API key in configuration")

        self.api_key = self.config['anthropic_api_key']
        self.model = self.config.get('anthropic_model', 'claude-sonnet-4-20250514')
        self.max_tokens = self.config.get('anthropic_max_tokens', 400)

        # Import here to avoid dependency if not using Claude
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

    def analyze_alert(self, alert: Dict[str, Any]) -> str:
        """
        Analyze alert using Claude AI

        Args:
            alert: Alert dictionary

        Returns:
            AI analysis string
        """
        try:
            prompt = self._build_analysis_prompt(alert)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{'role': 'user', 'content': prompt}]
            )

            analysis = response.content[0].text.strip()
            logger.info(f"Claude analysis received for {alert.get('host', 'Unknown')}")
            return analysis

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return self._get_fallback_analysis(alert)

    def _build_analysis_prompt(self, alert: Dict[str, Any]) -> str:
        """Build the analysis prompt for Claude"""
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

Provide in this format (max 5 lines total for messaging):
DIAGNOSIS: [What is happening and why]
IMPACT: [What services/users are affected]
ACTION 1: [Most important immediate step]
ACTION 2: [Second step if needed]
ROOT CAUSE: [Most likely cause]"""

    def _get_fallback_analysis(self, alert: Dict[str, Any]) -> str:
        """Provide basic analysis when Claude is unavailable"""
        return f"""DIAGNOSIS: Alert analysis unavailable - Claude API error
IMPACT: Manual investigation required
ACTION 1: Check device status: ssh {alert.get('hostip', 'device')}
ACTION 2: Review Zabbix dashboard for additional context
ROOT CAUSE: AI analysis unavailable - please investigate manually"""

    def health_check(self) -> bool:
        """Check if Claude API is accessible"""
        try:
            # Simple API call to verify connectivity
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{'role': 'user', 'content': 'test'}]
            )
            logger.info("Claude health check passed")
            return True
        except Exception as e:
            logger.error(f"Claude health check failed: {e}")
            return False
