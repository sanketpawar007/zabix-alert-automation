"""
Base Monitoring Provider Interface
Handles webhook reception and alert validation from monitoring systems
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseMonitoringProvider(ABC):
    """Abstract base class for monitoring system providers"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the monitoring provider with configuration

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
    def validate_webhook(self, request_headers: Dict[str, str], request_data: Any) -> bool:
        """
        Validate that the webhook request is authentic

        Args:
            request_headers: HTTP request headers
            request_data: Request body data

        Returns:
            True if webhook is valid, False otherwise
        """
        pass

    @abstractmethod
    def parse_alert(self, request_data: Any) -> Optional[Dict[str, Any]]:
        """
        Parse the webhook payload into a standardized alert format

        Args:
            request_data: Raw webhook payload

        Returns:
            Standardized alert dictionary or None if parsing fails
        """
        pass

    @abstractmethod
    def should_process_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Determine if this alert should be processed based on filters

        Args:
            alert: Parsed alert dictionary

        Returns:
            True if alert should be processed, False to skip
        """
        pass

    def get_provider_name(self) -> str:
        """Get the name of this provider"""
        return self.__class__.__name__.replace('Provider', '')
