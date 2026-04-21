"""
Microsoft Teams Messaging Provider
Enterprise-grade notifications via Teams Incoming Webhook
Privacy: Stays within your Microsoft tenant
"""
import logging
import requests
from typing import Dict, Any
from .base import BaseMessagingProvider

logger = logging.getLogger(__name__)


class TeamsProvider(BaseMessagingProvider):
    """Microsoft Teams webhook messaging provider"""

    def validate_config(self) -> None:
        """Validate Teams configuration"""
        if not self.config.get('teams_webhook_url'):
            raise ValueError("Missing teams_webhook_url in configuration")

        self.webhook_url = self.config['teams_webhook_url']
        self.timeout = self.config.get('teams_timeout', 10)

        # Validate webhook URL format
        if not self.webhook_url.startswith('https://'):
            raise ValueError("Teams webhook URL must start with https://")

    def send_message(self, alert: Dict[str, Any], ai_analysis: str) -> bool:
        """
        Send alert via Microsoft Teams

        Args:
            alert: Alert dictionary
            ai_analysis: AI analysis text

        Returns:
            True if sent successfully
        """
        try:
            card = self.format_message(alert, ai_analysis)

            response = requests.post(
                self.webhook_url,
                json=card,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()

            logger.info(f"Teams message sent successfully for {alert.get('host', 'Unknown')}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Teams message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Teams message: {e}")
            return False

    def format_message(self, alert: Dict[str, Any], ai_analysis: str) -> Dict[str, Any]:
        """
        Format alert as Microsoft Teams Adaptive Card

        Args:
            alert: Alert dictionary
            ai_analysis: AI analysis text

        Returns:
            Teams message card JSON
        """
        severity = alert.get('severity', 'Unknown')
        status = alert.get('status', 'Unknown')
        emoji = '✅' if status == 'RESOLVED' else self.get_severity_emoji(severity)

        # Choose theme color based on severity
        color_map = {
            'Disaster': 'attention',  # Red
            'High': 'warning',        # Yellow
            'Average': 'accent',      # Blue
            'Warning': 'good',        # Green
            'Information': 'default'  # Gray
        }
        theme_color = color_map.get(severity, 'default')

        # Parse AI analysis into sections
        ai_lines = ai_analysis.split('\n')

        # Build Adaptive Card
        card = {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": f"{emoji} JUNIPER NETWORK ALERT",
                            "weight": "bolder",
                            "size": "large",
                            "color": theme_color
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Device:", "value": alert.get('host', 'Unknown')},
                                {"title": "IP:", "value": alert.get('hostip', 'Unknown')},
                                {"title": "Problem:", "value": alert.get('name', 'Unknown')},
                                {"title": "Severity:", "value": severity},
                                {"title": "Status:", "value": status},
                                {"title": "Value:", "value": str(alert.get('value', 'N/A'))},
                                {"title": "Time:", "value": alert.get('time', 'N/A')}
                            ]
                        },
                        {
                            "type": "TextBlock",
                            "text": "🤖 AI Analysis",
                            "weight": "bolder",
                            "size": "medium",
                            "spacing": "medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": ai_analysis,
                            "wrap": True,
                            "spacing": "small"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Event ID: {alert.get('eventid', 'N/A')}",
                            "size": "small",
                            "color": "default",
                            "spacing": "medium"
                        }
                    ]
                }
            }]
        }

        return card

    def health_check(self) -> bool:
        """
        Check if Teams webhook is accessible
        Note: Teams doesn't have a ping endpoint, so we validate URL format only

        Returns:
            True if configuration looks valid
        """
        try:
            # Validate URL format
            if not self.webhook_url.startswith('https://'):
                logger.error("Teams webhook URL invalid - must be HTTPS")
                return False

            if 'webhook.office.com' not in self.webhook_url:
                logger.warning("Teams webhook URL doesn't look standard")
                return False

            logger.info("Teams health check passed (URL format valid)")
            return True

        except Exception as e:
            logger.error(f"Teams health check failed: {e}")
            return False
