"""
Email (SMTP) Messaging Provider
Privacy-first notifications via internal or external SMTP server
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from .base import BaseMessagingProvider

logger = logging.getLogger(__name__)


class EmailProvider(BaseMessagingProvider):
    """Email SMTP messaging provider"""

    def validate_config(self) -> None:
        """Validate Email configuration"""
        required_fields = ['smtp_server', 'smtp_port', 'alert_recipients']
        missing = [f for f in required_fields if not self.config.get(f)]

        if missing:
            raise ValueError(f"Missing Email configuration: {', '.join(missing)}")

        self.smtp_server = self.config['smtp_server']
        self.smtp_port = int(self.config['smtp_port'])
        self.smtp_username = self.config.get('smtp_username', '')
        self.smtp_password = self.config.get('smtp_password', '')
        self.smtp_use_tls = self.config.get('smtp_use_tls', 'true').lower() == 'true'
        self.smtp_use_ssl = self.config.get('smtp_use_ssl', 'false').lower() == 'true'
        self.from_email = self.config.get('smtp_from_email', 'juniper-alerts@localhost')

        # Parse recipient emails
        recipients = self.config['alert_recipients']
        if isinstance(recipients, str):
            self.recipients = [r.strip() for r in recipients.split(',') if r.strip()]
        else:
            self.recipients = recipients

        if not self.recipients:
            raise ValueError("No email recipients configured")

    def send_message(self, alert: Dict[str, Any], ai_analysis: str) -> bool:
        """
        Send alert via email

        Args:
            alert: Alert dictionary
            ai_analysis: AI analysis text

        Returns:
            True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self._get_subject(alert)
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.recipients)

            # Create HTML and plain text versions
            text_body = self.format_message(alert, ai_analysis)
            html_body = self._format_html(alert, ai_analysis)

            # Attach both versions
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)

            # Connect and send
            if self.smtp_use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                if self.smtp_use_tls:
                    server.starttls()

            # Login if credentials provided
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            # Send email
            server.sendmail(self.from_email, self.recipients, msg.as_string())
            server.quit()

            logger.info(f"Email sent to {len(self.recipients)} recipient(s)")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def format_message(self, alert: Dict[str, Any], ai_analysis: str) -> str:
        """
        Format alert as plain text email

        Args:
            alert: Alert dictionary
            ai_analysis: AI analysis text

        Returns:
            Formatted plain text message
        """
        severity = alert.get('severity', 'Unknown')
        status = alert.get('status', 'Unknown')
        emoji = '✅' if status == 'RESOLVED' else self.get_severity_emoji(severity)

        message = f"""{emoji} JUNIPER NETWORK ALERT
{'=' * 70}

ALERT DETAILS
{'-' * 70}
Device:    {alert.get('host', 'Unknown')}
IP:        {alert.get('hostip', 'Unknown')}
Problem:   {alert.get('name', 'Unknown')}
Severity:  {severity}
Status:    {status}
Value:     {alert.get('value', 'N/A')}
Time:      {alert.get('time', 'N/A')}

AI ANALYSIS
{'-' * 70}
{ai_analysis}

{'-' * 70}
Event ID: {alert.get('eventid', 'N/A')}

---
This is an automated alert from the Juniper AI Alert System
"""
        return message

    def _format_html(self, alert: Dict[str, Any], ai_analysis: str) -> str:
        """Format alert as HTML email"""
        severity = alert.get('severity', 'Unknown')
        status = alert.get('status', 'Unknown')
        emoji = '✅' if status == 'RESOLVED' else self.get_severity_emoji(severity)

        # Color based on severity
        color_map = {
            'Disaster': '#d32f2f',
            'High': '#f57c00',
            'Average': '#fbc02d',
            'Warning': '#689f38',
            'Information': '#1976d2',
            'Not classified': '#757575'
        }
        header_color = color_map.get(severity, '#757575')

        # Format AI analysis with line breaks
        ai_html = ai_analysis.replace('\n', '<br>')

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ background-color: {header_color}; color: white; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .content {{ padding: 20px; }}
        .detail-row {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
        .label {{ font-weight: bold; color: #555; width: 120px; display: inline-block; }}
        .value {{ color: #222; }}
        .section-title {{ font-size: 18px; font-weight: bold; margin: 20px 0 10px 0; color: #333; }}
        .ai-analysis {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #2196f3; margin: 10px 0; line-height: 1.6; }}
        .footer {{ text-align: center; padding: 15px; font-size: 12px; color: #999; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{emoji} JUNIPER NETWORK ALERT</h1>
        </div>
        <div class="content">
            <h2 class="section-title">Alert Details</h2>
            <div class="detail-row">
                <span class="label">Device:</span>
                <span class="value">{alert.get('host', 'Unknown')}</span>
            </div>
            <div class="detail-row">
                <span class="label">IP Address:</span>
                <span class="value">{alert.get('hostip', 'Unknown')}</span>
            </div>
            <div class="detail-row">
                <span class="label">Problem:</span>
                <span class="value">{alert.get('name', 'Unknown')}</span>
            </div>
            <div class="detail-row">
                <span class="label">Severity:</span>
                <span class="value">{severity}</span>
            </div>
            <div class="detail-row">
                <span class="label">Status:</span>
                <span class="value">{status}</span>
            </div>
            <div class="detail-row">
                <span class="label">Value:</span>
                <span class="value">{alert.get('value', 'N/A')}</span>
            </div>
            <div class="detail-row">
                <span class="label">Time:</span>
                <span class="value">{alert.get('time', 'N/A')}</span>
            </div>

            <h2 class="section-title">🤖 AI Analysis</h2>
            <div class="ai-analysis">
                {ai_html}
            </div>
        </div>
        <div class="footer">
            Event ID: {alert.get('eventid', 'N/A')}<br>
            <small>Automated alert from Juniper AI Alert System</small>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _get_subject(self, alert: Dict[str, Any]) -> str:
        """Generate email subject line"""
        severity = alert.get('severity', 'Unknown')
        status = alert.get('status', 'Unknown')
        host = alert.get('host', 'Unknown')
        problem = alert.get('name', 'Alert')

        emoji = '✅' if status == 'RESOLVED' else self.get_severity_emoji(severity)

        return f"{emoji} [{severity}] {host} - {problem}"

    def health_check(self) -> bool:
        """
        Check SMTP server connectivity

        Returns:
            True if SMTP server is accessible
        """
        try:
            # Try to connect to SMTP server
            if self.smtp_use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=5)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=5)
                if self.smtp_use_tls:
                    server.starttls()

            # Try to login if credentials provided
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            server.quit()

            logger.info("Email SMTP health check passed")
            return True

        except Exception as e:
            logger.error(f"Email SMTP health check failed: {e}")
            return False
