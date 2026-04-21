"""
Base AI Provider Interface
All AI providers (Claude, Ollama, OpenAI, etc.) must implement this interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAIProvider(ABC):
    """Abstract base class for AI providers"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the AI provider with configuration

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
    def analyze_alert(self, alert: Dict[str, Any]) -> str:
        """
        Analyze a network alert and provide diagnosis and recommendations

        Args:
            alert: Dictionary containing alert information:
                - host: Device hostname
                - hostip: Device IP address
                - name: Alert name/description
                - severity: Alert severity level
                - status: PROBLEM or RESOLVED
                - value: Metric value that triggered alert
                - trigger: Trigger name
                - time: Timestamp
                - eventid: Unique event identifier

        Returns:
            String containing AI analysis in a structured format
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the AI provider is accessible and functioning

        Returns:
            True if provider is healthy, False otherwise
        """
        pass

    def get_provider_name(self) -> str:
        """Get the name of this provider"""
        return self.__class__.__name__.replace('Provider', '')
