"""
Settings Manager
Loads configuration from environment variables and creates provider instances
"""
import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Settings:
    """Application settings manager"""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize settings from environment

        Args:
            env_file: Optional path to .env file (default: .env in current dir)
        """
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        self._load_settings()

    def _load_settings(self) -> None:
        """Load all settings from environment"""

        # ===== PROVIDER SELECTION =====
        self.ai_provider = os.getenv('PROVIDER_AI', 'ollama').lower()
        self.messaging_provider = os.getenv('PROVIDER_MESSAGING', 'telegram').lower()
        self.monitoring_provider = os.getenv('PROVIDER_MONITORING', 'zabbix').lower()

        # ===== FLASK SETTINGS =====
        self.flask_host = os.getenv('FLASK_HOST', '127.0.0.1')
        self.flask_port = int(os.getenv('FLASK_PORT', '5001'))
        self.flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

        # ===== MONITORING SETTINGS =====
        self.webhook_secret = os.getenv('WEBHOOK_SECRET', '')
        self.min_severity = os.getenv('MIN_SEVERITY', 'High')

        # ===== OLLAMA SETTINGS =====
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.ollama_timeout = int(os.getenv('OLLAMA_TIMEOUT', '60'))
        self.ollama_temperature = float(os.getenv('OLLAMA_TEMPERATURE', '0.7'))
        self.ollama_max_tokens = int(os.getenv('OLLAMA_MAX_TOKENS', '400'))

        # ===== CLAUDE SETTINGS =====
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        self.anthropic_model = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
        self.anthropic_max_tokens = int(os.getenv('ANTHROPIC_MAX_TOKENS', '400'))

        # ===== TELEGRAM SETTINGS =====
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_ids = os.getenv('TELEGRAM_CHAT_IDS', '')
        self.telegram_timeout = int(os.getenv('TELEGRAM_TIMEOUT', '10'))
        self.telegram_parse_mode = os.getenv('TELEGRAM_PARSE_MODE', 'Markdown')

        # ===== TWILIO SETTINGS =====
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_whatsapp_from = os.getenv('TWILIO_WHATSAPP_FROM', '')
        self.whatsapp_recipients = os.getenv('WHATSAPP_RECIPIENTS', '')

        # ===== LOGGING SETTINGS =====
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/alert-service.log')

        # ===== SIMULATOR SETTINGS =====
        self.simulator_require_auth = os.getenv('SIMULATOR_REQUIRE_AUTH', 'False').lower() == 'true'

    def get_ai_config(self) -> Dict[str, Any]:
        """Get configuration for AI provider"""
        if self.ai_provider == 'ollama':
            return {
                'ollama_base_url': self.ollama_base_url,
                'ollama_model': self.ollama_model,
                'ollama_timeout': self.ollama_timeout,
                'ollama_temperature': self.ollama_temperature,
                'ollama_max_tokens': self.ollama_max_tokens
            }
        elif self.ai_provider == 'claude':
            return {
                'anthropic_api_key': self.anthropic_api_key,
                'anthropic_model': self.anthropic_model,
                'anthropic_max_tokens': self.anthropic_max_tokens
            }
        else:
            raise ValueError(f"Unknown AI provider: {self.ai_provider}")

    def get_messaging_config(self) -> Dict[str, Any]:
        """Get configuration for messaging provider"""
        if self.messaging_provider == 'telegram':
            return {
                'telegram_bot_token': self.telegram_bot_token,
                'telegram_chat_ids': self.telegram_chat_ids,
                'telegram_timeout': self.telegram_timeout,
                'telegram_parse_mode': self.telegram_parse_mode
            }
        elif self.messaging_provider == 'twilio':
            return {
                'twilio_account_sid': self.twilio_account_sid,
                'twilio_auth_token': self.twilio_auth_token,
                'twilio_whatsapp_from': self.twilio_whatsapp_from,
                'whatsapp_recipients': self.whatsapp_recipients
            }
        else:
            raise ValueError(f"Unknown messaging provider: {self.messaging_provider}")

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get configuration for monitoring provider"""
        config = {
            'webhook_secret': self.webhook_secret,
            'min_severity': self.min_severity
        }

        if self.monitoring_provider == 'simulator':
            config['simulator_require_auth'] = self.simulator_require_auth

        return config

    def validate(self) -> None:
        """
        Validate that all required settings are present
        Raises ValueError if validation fails
        """
        errors = []

        # Validate webhook secret
        if not self.webhook_secret and self.monitoring_provider != 'simulator':
            errors.append("WEBHOOK_SECRET is required")

        # Validate AI provider config
        if self.ai_provider == 'ollama':
            if not self.ollama_model:
                errors.append("OLLAMA_MODEL is required when using Ollama")
        elif self.ai_provider == 'claude':
            if not self.anthropic_api_key:
                errors.append("ANTHROPIC_API_KEY is required when using Claude")

        # Validate messaging provider config
        if self.messaging_provider == 'telegram':
            if not self.telegram_bot_token:
                errors.append("TELEGRAM_BOT_TOKEN is required when using Telegram")
            if not self.telegram_chat_ids:
                errors.append("TELEGRAM_CHAT_IDS is required when using Telegram")
        elif self.messaging_provider == 'twilio':
            if not self.twilio_account_sid:
                errors.append("TWILIO_ACCOUNT_SID is required when using Twilio")
            if not self.twilio_auth_token:
                errors.append("TWILIO_AUTH_TOKEN is required when using Twilio")

        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

        logger.info("Configuration validation passed")
        logger.info(f"Providers: AI={self.ai_provider}, Messaging={self.messaging_provider}, Monitoring={self.monitoring_provider}")

    def __repr__(self) -> str:
        """String representation of settings"""
        return (
            f"Settings(ai={self.ai_provider}, "
            f"messaging={self.messaging_provider}, "
            f"monitoring={self.monitoring_provider})"
        )
