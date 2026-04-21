"""
Zabbix Monitoring Provider
Handles webhook reception from Zabbix monitoring system
"""
import logging
import hmac
import hashlib
from typing import Dict, Any, Optional
from .base import BaseMonitoringProvider

logger = logging.getLogger(__name__)


class ZabbixProvider(BaseMonitoringProvider):
    """Zabbix webhook monitoring provider"""

    def validate_config(self) -> None:
        """Validate Zabbix configuration"""
        if not self.config.get('webhook_secret'):
            raise ValueError("Missing webhook_secret in configuration")

        self.webhook_secret = self.config['webhook_secret']
        self.min_severity = self.config.get('min_severity', 'High')

        # Severity ordering for filtering
        self.severity_order = {
            'Not classified': 0,
            'Information': 1,
            'Warning': 2,
            'Average': 3,
            'High': 4,
            'Disaster': 5
        }

    def validate_webhook(self, request_headers: Dict[str, str], request_data: Any) -> bool:
        """
        Validate webhook authenticity using HMAC secret

        Args:
            request_headers: HTTP request headers
            request_data: Request body (not used for Zabbix, uses header)

        Returns:
            True if webhook is valid
        """
        provided_secret = request_headers.get('X-Webhook-Secret', '')

        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(provided_secret, self.webhook_secret)

        if not is_valid:
            logger.warning(f"Invalid webhook secret from {request_headers.get('X-Real-IP', 'Unknown')}")

        return is_valid

    def parse_alert(self, request_data: Any) -> Optional[Dict[str, Any]]:
        """
        Parse Zabbix webhook payload

        Args:
            request_data: JSON payload from Zabbix

        Returns:
            Standardized alert dictionary
        """
        try:
            if not isinstance(request_data, dict):
                logger.error("Invalid Zabbix payload - not a dictionary")
                return None

            # Zabbix sends these fields via webhook parameters
            alert = {
                'host': request_data.get('host', 'Unknown'),
                'hostip': request_data.get('hostip', 'Unknown'),
                'name': request_data.get('name', 'Unknown'),
                'severity': request_data.get('severity', 'Unknown'),
                'status': request_data.get('status', 'Unknown'),
                'value': request_data.get('value', 'N/A'),
                'trigger': request_data.get('trigger', 'N/A'),
                'eventid': request_data.get('eventid', 'N/A'),
                'time': request_data.get('time', 'N/A'),
                'recovery': request_data.get('recovery', ''),
                'tags': request_data.get('tags', '')
            }

            logger.info(
                f"Parsed Zabbix alert: {alert['host']} | "
                f"{alert['severity']} | {alert['status']}"
            )

            return alert

        except Exception as e:
            logger.error(f"Failed to parse Zabbix alert: {e}")
            return None

    def should_process_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Determine if alert should be processed based on severity filter

        Args:
            alert: Parsed alert dictionary

        Returns:
            True if alert meets minimum severity threshold
        """
        severity = alert.get('severity', 'Unknown')
        alert_level = self.severity_order.get(severity, 0)
        min_level = self.severity_order.get(self.min_severity, 4)

        should_process = alert_level >= min_level

        if not should_process:
            logger.info(
                f"Alert filtered out (severity {severity} < {self.min_severity}): "
                f"{alert.get('host', 'Unknown')}"
            )

        return should_process

    def get_severity_level(self, severity: str) -> int:
        """
        Get numeric severity level

        Args:
            severity: Severity string

        Returns:
            Numeric level (0-5)
        """
        return self.severity_order.get(severity, 0)
