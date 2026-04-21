"""
Telegram Messaging Provider
Free alternative to WhatsApp - uses Telegram Bot API
"""
import logging
import requests
from typing import Dict, Any, List
from .base import BaseMessagingProvider

logger = logging.getLogger(__name__)


class TelegramProvider(BaseMessagingProvider):
    """Telegram Bot messaging provider"""

    def validate_config(self) -> None:
        """Validate Telegram configuration"""
        required_fields = ['telegram_bot_token', 'telegram_chat_ids']
        missing = [f for f in required_fields if not self.config.get(f)]

        if missing:
            raise ValueError(f"Missing Telegram configuration: {', '.join(missing)}")

        self.bot_token = self.config['telegram_bot_token']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        # Parse chat IDs (can be comma-separated string or list)
        chat_ids = self.config['telegram_chat_ids']
        if isinstance(chat_ids, str):
            self.chat_ids = [cid.strip() for cid in chat_ids.split(',') if cid.strip()]
        else:
            self.chat_ids = chat_ids

        if not self.chat_ids:
            raise ValueError("No Telegram chat IDs configured")

        self.timeout = self.config.get('telegram_timeout', 10)
        self.parse_mode = self.config.get('telegram_parse_mode', 'Markdown')

    def send_message(self, alert: Dict[str, Any], ai_analysis: str) -> bool:
        """
        Send alert message via Telegram

        Args:
            alert: Alert dictionary
            ai_analysis: AI analysis text

        Returns:
            True if sent to at least one recipient successfully
        """
        message = self.format_message(alert, ai_analysis)
        success_count = 0

        for chat_id in self.chat_ids:
            try:
                response = requests.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        'chat_id': chat_id,
                        'text': message,
                        'parse_mode': self.parse_mode,
                        'disable_web_page_preview': True
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()

                logger.info(f"Telegram message sent to chat_id: {chat_id}")
                success_count += 1

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error sending to {chat_id}: {e}")

        return success_count > 0

    def format_message(self, alert: Dict[str, Any], ai_analysis: str) -> str:
        """
        Format alert message for Telegram (supports Markdown)

        Args:
            alert: Alert dictionary
            ai_analysis: AI analysis text

        Returns:
            Formatted Telegram message
        """
        severity = alert.get('severity', 'Unknown')
        status = alert.get('status', 'Unknown')
        emoji = '✅' if status == 'RESOLVED' else self.get_severity_emoji(severity)

        # Escape special characters for Markdown
        def escape_md(text: str) -> str:
            """Escape special Markdown characters"""
            if text is None:
                return 'N/A'
            special_chars = '_*[]()~`>#+-=|{}.!'
            for char in special_chars:
                text = str(text).replace(char, '\\' + char)
            return text

        message = f"""{emoji} *JUNIPER NETWORK ALERT*
{'━' * 26}
🖥️ *Device:*   {escape_md(alert.get('host', 'Unknown'))}
🌐 *IP:*       `{alert.get('hostip', 'Unknown')}`
⚠️ *Problem:*  {escape_md(alert.get('name', 'Unknown'))}
📊 *Severity:* {escape_md(severity)}
📡 *Status:*   {escape_md(status)}
📈 *Value:*    {escape_md(alert.get('value', 'N/A'))}
🕐 *Time:*     {escape_md(alert.get('time', 'N/A'))}
{'━' * 26}
🤖 *AI Analysis:*
{ai_analysis}
{'━' * 26}
Event ID: {escape_md(alert.get('eventid', 'N/A'))}"""

        return message

    def health_check(self) -> bool:
        """
        Check if Telegram Bot API is accessible

        Returns:
            True if bot is accessible, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/getMe",
                timeout=5
            )
            response.raise_for_status()

            bot_info = response.json()
            if bot_info.get('ok'):
                bot_username = bot_info.get('result', {}).get('username', 'Unknown')
                logger.info(f"Telegram health check passed - bot: @{bot_username}")
                return True
            else:
                logger.error("Telegram health check failed - invalid response")
                return False

        except Exception as e:
            logger.error(f"Telegram health check failed: {e}")
            return False

    def get_bot_info(self) -> Dict[str, Any]:
        """
        Get information about the configured bot

        Returns:
            Dictionary with bot information
        """
        try:
            response = requests.get(
                f"{self.base_url}/getMe",
                timeout=5
            )
            response.raise_for_status()
            return response.json().get('result', {})
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")
            return {}
