"""
Base Messaging Provider Interface
All messaging providers (Telegram, WhatsApp, Slack, etc.) must implement this interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseMessagingProvider(ABC):
    """Abstract base class for messaging providers"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the messaging provider with configuration

        Args:
            config: Dictionary containing provider-specific configuration
        """
        self.config = config
        self.validate_config()

    @abstractmethod
    def validate_config(self) -> None:
        """
        Validate that all required configuration parameters are present
        Raises ValueError if configuration is invalid
        """
        pass

    @abstractmethod
    def send_message(self, alert: Dict[str, Any], ai_analysis: str) -> bool:
        """
        Send an alert message to configured recipients

        Args:
            alert: Dictionary containing alert information
            ai_analysis: AI-generated analysis text

        Returns:
            True if message sent successfully, False otherwise
        """
        pass

    @abstractmethod
    def format_message(self, alert: Dict[str, Any], ai_analysis: str) -> str:
        """
        Format alert and AI analysis into a message suitable for this provider

        Args:
            alert: Dictionary containing alert information
            ai_analysis: AI-generated analysis text

        Returns:
            Formatted message string
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the messaging provider is accessible and functioning

        Returns:
            True if provider is healthy, False otherwise
        """
        pass

    def get_provider_name(self) -> str:
        """Get the name of this provider"""
        return self.__class__.__name__.replace('Provider', '')

    def get_severity_emoji(self, severity: str) -> str:
        """
        Get emoji representation for alert severity

        Args:
            severity: Severity level string

        Returns:
            Emoji character
        """
        emoji_map = {
            'Disaster': '🚨',
            'High': '🔴',
            'Average': '🟠',
            'Warning': '🟡',
            'Information': '🔵',
            'Not classified': '⚪'
        }
        return emoji_map.get(severity, '⚠️')
