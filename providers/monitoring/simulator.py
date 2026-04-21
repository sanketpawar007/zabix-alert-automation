"""
Alert Simulator Provider
Simulates monitoring system webhooks for development/testing
No authentication required - FOR TESTING ONLY
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseMonitoringProvider

logger = logging.getLogger(__name__)


class SimulatorProvider(BaseMonitoringProvider):
    """Development alert simulator provider"""

    def validate_config(self) -> None:
        """Validate simulator configuration"""
        # Simulator doesn't require strict config
        self.require_auth = self.config.get('simulator_require_auth', False)
        self.test_secret = self.config.get('webhook_secret', 'test-secret-123')

        logger.warning(
            "⚠️  SIMULATOR MODE ACTIVE - NOT FOR PRODUCTION USE ⚠️"
        )

    def validate_webhook(self, request_headers: Dict[str, str], request_data: Any) -> bool:
        """
        Minimal validation for simulator mode

        Args:
            request_headers: HTTP request headers
            request_data: Request body

        Returns:
            True (always valid in simulator mode, or check test secret)
        """
        if not self.require_auth:
            logger.info("Simulator accepting webhook without authentication")
            return True

        # Optional: check test secret if enabled
        provided_secret = request_headers.get('X-Webhook-Secret', '')
        is_valid = provided_secret == self.test_secret

        if not is_valid:
            logger.warning("Simulator rejected webhook - invalid test secret")

        return is_valid

    def parse_alert(self, request_data: Any) -> Optional[Dict[str, Any]]:
        """
        Parse simulated alert - accepts flexible format

        Args:
            request_data: JSON payload

        Returns:
            Standardized alert dictionary
        """
        try:
            if not isinstance(request_data, dict):
                logger.error("Invalid simulator payload - not a dictionary")
                return None

            # Accept both Zabbix-style and simplified test formats
            alert = {
                'host': request_data.get('host', 'test-device-01'),
                'hostip': request_data.get('hostip', '192.168.1.100'),
                'name': request_data.get('name', 'Test Alert'),
                'severity': request_data.get('severity', 'High'),
                'status': request_data.get('status', 'PROBLEM'),
                'value': request_data.get('value', 'test-value'),
                'trigger': request_data.get('trigger', 'Test Trigger'),
                'eventid': request_data.get('eventid', '99999'),
                'time': request_data.get('time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'recovery': request_data.get('recovery', ''),
                'tags': request_data.get('tags', '')
            }

            logger.info(
                f"[SIMULATOR] Parsed alert: {alert['host']} | "
                f"{alert['severity']} | {alert['status']}"
            )

            return alert

        except Exception as e:
            logger.error(f"Failed to parse simulator alert: {e}")
            return None

    def should_process_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Simulator processes all alerts (no filtering)

        Args:
            alert: Parsed alert dictionary

        Returns:
            Always True in simulator mode
        """
        logger.info(f"[SIMULATOR] Processing alert: {alert.get('name', 'Unknown')}")
        return True

    def generate_sample_alert(self, alert_type: str = 'interface_down') -> Dict[str, Any]:
        """
        Generate sample alert for testing

        Args:
            alert_type: Type of alert to generate

        Returns:
            Sample alert dictionary
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        samples = {
            'interface_down': {
                'host': 'juniper-core-router-01',
                'hostip': '192.168.1.1',
                'name': 'Interface ge-0/0/1 is DOWN',
                'severity': 'Disaster',
                'status': 'PROBLEM',
                'value': 'down(2)',
                'trigger': 'Interface operational status changed to DOWN',
                'eventid': '12345',
                'time': current_time
            },
            'high_cpu': {
                'host': 'juniper-edge-router-02',
                'hostip': '192.168.1.2',
                'name': 'High CPU utilization - 91%',
                'severity': 'High',
                'status': 'PROBLEM',
                'value': '91',
                'trigger': 'CPU utilization above 85% for 5 minutes',
                'eventid': '12346',
                'time': current_time
            },
            'memory_high': {
                'host': 'juniper-distribution-switch-01',
                'hostip': '192.168.1.3',
                'name': 'High memory utilization - 93%',
                'severity': 'High',
                'status': 'PROBLEM',
                'value': '93',
                'trigger': 'Memory utilization above 90%',
                'eventid': '12347',
                'time': current_time
            },
            'resolved': {
                'host': 'juniper-core-router-01',
                'hostip': '192.168.1.1',
                'name': 'Interface ge-0/0/1 is DOWN',
                'severity': 'Disaster',
                'status': 'RESOLVED',
                'value': 'up(1)',
                'trigger': 'Interface operational status changed to DOWN',
                'eventid': '12345',
                'time': current_time,
                'recovery': current_time
            }
        }

        return samples.get(alert_type, samples['interface_down'])
