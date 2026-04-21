"""
Twilio WhatsApp Messaging Provider
Production messaging via Twilio WhatsApp Business API
"""
import logging
from typing import Dict, Any
from .base import BaseMessagingProvider

logger = logging.getLogger(__name__)


class TwilioWhatsAppProvider(BaseMessagingProvider):
    """Twilio WhatsApp messaging provider"""

    def validate_config(self) -> None:
        """Validate Twilio configuration"""
        required_fields = ['twilio_account_sid', 'twilio_auth_token',
                          'twilio_whatsapp_from', 'whatsapp_recipients']
        missing = [f for f in required_fields if not self.config.get(f)]

        if missing:
            raise ValueError(f"Missing Twilio configuration: {', '.join(missing)}")

        # Import Twilio here to avoid dependency if not using this provider
        try:
            from twilio.rest import Client
            self.client = Client(
                self.config['twilio_account_sid'],
                self.config['twilio_auth_token']
            )
        except ImportError:
            raise ImportError("twilio package not installed. Run: pip install twilio")

        self.from_number = self.config['twilio_whatsapp_from']

        # Parse recipient numbers
        recipients = self.config['whatsapp_recipients']
        if isinstance(recipients, str):
            self.recipients = [r.strip() for r in recipients.split(',') if r.strip()]
        else:
            self.recipients = recipients

    def send_message(self, alert: Dict[str, Any], ai_analysis: str) -> bool:
        """
        Send alert via WhatsApp using Twilio

        Args:
            alert: Alert dictionary
            ai_analysis: AI analysis text

        Returns:
            True if sent successfully
        """
        message = self.format_message(alert, ai_analysis)
        success_count = 0

        for recipient in self.recipients:
            try:
                self.client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=recipient
                )
                logger.info(f"WhatsApp message sent to {recipient}")
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send WhatsApp to {recipient}: {e}")

        return success_count > 0

    def format_message(self, alert: Dict[str, Any], ai_analysis: str) -> str:
        """Format message for WhatsApp"""
        severity = alert.get('severity', 'Unknown')
        status = alert.get('status', 'Unknown')
        emoji = '✅' if status == 'RESOLVED' else self.get_severity_emoji(severity)

        message = f"""{emoji} *JUNIPER NETWORK ALERT*
{'━' * 26}
🖥️ *Device:*   {alert.get('host', 'Unknown')}
🌐 *IP:*       {alert.get('hostip', 'Unknown')}
⚠️ *Problem:*  {alert.get('name', 'Unknown')}
📊 *Severity:* {severity}
📡 *Status:*   {status}
📈 *Value:*    {alert.get('value', 'N/A')}
🕐 *Time:*     {alert.get('time', 'N/A')}
{'━' * 26}
🤖 *AI Analysis:*
{ai_analysis}
{'━' * 26}
Event ID: {alert.get('eventid', 'N/A')}"""

        return message

    def health_check(self) -> bool:
        """Check Twilio account status"""
        try:
            # Verify account by fetching account info
            account = self.client.api.accounts(self.config['twilio_account_sid']).fetch()
            logger.info(f"Twilio health check passed - account: {account.friendly_name}")
            return True
        except Exception as e:
            logger.error(f"Twilio health check failed: {e}")
            return False
