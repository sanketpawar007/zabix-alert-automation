"""
Juniper Network AI Alert System
Main Flask application - receives alerts, analyzes with AI, sends notifications

Flexible provider-based architecture:
- AI: Ollama (local), Claude (production), or others
- Messaging: Telegram (free), WhatsApp/Twilio (production), or others
- Monitoring: Zabbix (production), Simulator (development)
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, abort

from config.settings import Settings
from providers.ai.ollama import OllamaProvider
from providers.ai.claude import ClaudeProvider
from providers.messaging.telegram import TelegramProvider
from providers.messaging.twilio_whatsapp import TwilioWhatsAppProvider
from providers.monitoring.zabbix import ZabbixProvider
from providers.monitoring.simulator import SimulatorProvider

# ══════════════════════════════════════════════════════════════════════════════
# APPLICATION SETUP
# ══════════════════════════════════════════════════════════════════════════════

app = Flask(__name__)

# Load configuration
try:
    settings = Settings()
    settings.validate()
except Exception as e:
    print(f"❌ Configuration error: {e}")
    print("Please check your .env file and try again.")
    exit(1)

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# PROVIDER INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════

def init_ai_provider():
    """Initialize AI provider based on configuration"""
    provider_name = settings.ai_provider
    config = settings.get_ai_config()

    if provider_name == 'ollama':
        return OllamaProvider(config)
    elif provider_name == 'claude':
        return ClaudeProvider(config)
    else:
        raise ValueError(f"Unknown AI provider: {provider_name}")


def init_messaging_provider():
    """Initialize messaging provider based on configuration"""
    provider_name = settings.messaging_provider
    config = settings.get_messaging_config()

    if provider_name == 'telegram':
        return TelegramProvider(config)
    elif provider_name == 'twilio':
        return TwilioWhatsAppProvider(config)
    else:
        raise ValueError(f"Unknown messaging provider: {provider_name}")


def init_monitoring_provider():
    """Initialize monitoring provider based on configuration"""
    provider_name = settings.monitoring_provider
    config = settings.get_monitoring_config()

    if provider_name == 'zabbix':
        return ZabbixProvider(config)
    elif provider_name == 'simulator':
        return SimulatorProvider(config)
    else:
        raise ValueError(f"Unknown monitoring provider: {provider_name}")


# Initialize all providers
try:
    ai_provider = init_ai_provider()
    messaging_provider = init_messaging_provider()
    monitoring_provider = init_monitoring_provider()

    logger.info("=" * 70)
    logger.info("🚀 Juniper AI Alert System Starting")
    logger.info("=" * 70)
    logger.info(f"AI Provider:         {ai_provider.get_provider_name()}")
    logger.info(f"Messaging Provider:  {messaging_provider.get_provider_name()}")
    logger.info(f"Monitoring Provider: {monitoring_provider.get_provider_name()}")
    logger.info("=" * 70)

except Exception as e:
    logger.error(f"Failed to initialize providers: {e}")
    exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns service status and provider health
    """
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'providers': {
            'ai': ai_provider.get_provider_name(),
            'messaging': messaging_provider.get_provider_name(),
            'monitoring': monitoring_provider.get_provider_name()
        },
        'version': '1.0.0'
    }

    # Check provider health
    provider_health = {
        'ai_healthy': ai_provider.health_check(),
        'messaging_healthy': messaging_provider.health_check()
    }

    health_status['provider_health'] = provider_health

    # Overall health is good if at least AI and messaging are healthy
    all_healthy = provider_health['ai_healthy'] and provider_health['messaging_healthy']
    health_status['status'] = 'healthy' if all_healthy else 'degraded'

    status_code = 200 if all_healthy else 503

    logger.info(f"Health check: {health_status['status']}")
    return jsonify(health_status), status_code


@app.route('/webhook/zabbix', methods=['POST'])
def receive_alert():
    """
    Main webhook endpoint
    Receives alerts from monitoring system -> AI analysis -> send notification
    """
    try:
        # Step 1: Validate webhook authenticity
        if not monitoring_provider.validate_webhook(dict(request.headers), request.get_json(silent=True)):
            logger.warning(f"Unauthorized webhook attempt from {request.remote_addr}")
            abort(403)

        # Step 2: Parse request body
        raw_data = request.get_json(silent=True)
        if not raw_data:
            logger.error("Empty or invalid JSON body received")
            abort(400)

        # Step 3: Parse alert into standardized format
        alert = monitoring_provider.parse_alert(raw_data)
        if not alert:
            logger.error("Failed to parse alert")
            return jsonify({'status': 'error', 'message': 'Invalid alert format'}), 400

        host = alert.get('host', 'Unknown')
        severity = alert.get('severity', 'Unknown')
        status = alert.get('status', 'Unknown')

        logger.info(f"📨 Alert received: {host} | {severity} | {status}")

        # Step 4: Check if alert should be processed
        if not monitoring_provider.should_process_alert(alert):
            logger.info(f"Alert filtered out: {host}")
            return jsonify({'status': 'filtered', 'reason': 'below minimum severity'}), 200

        # Step 5: Get AI analysis
        try:
            logger.info(f"🤖 Requesting AI analysis from {ai_provider.get_provider_name()}...")
            ai_analysis = ai_provider.analyze_alert(alert)
            logger.info(f"✅ AI analysis received for {host}")
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            ai_analysis = "AI analysis unavailable. Please investigate manually."

        # Step 6: Send notification
        try:
            logger.info(f"📤 Sending notification via {messaging_provider.get_provider_name()}...")
            success = messaging_provider.send_message(alert, ai_analysis)

            if success:
                logger.info(f"✅ Notification sent successfully for {host}")
                return jsonify({
                    'status': 'success',
                    'host': host,
                    'eventid': alert.get('eventid', 'N/A')
                }), 200
            else:
                logger.error(f"Failed to send notification for {host}")
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to send notification'
                }), 500

        except Exception as e:
            logger.error(f"Notification send failed: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error processing alert: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


@app.route('/test/alert', methods=['POST'])
def test_alert():
    """
    Test endpoint - generate and process a sample alert
    Useful for development and testing
    """
    try:
        # Get alert type from request or use default
        data = request.get_json(silent=True) or {}
        alert_type = data.get('type', 'interface_down')

        # Generate sample alert if using simulator
        if isinstance(monitoring_provider, SimulatorProvider):
            alert = monitoring_provider.generate_sample_alert(alert_type)
        else:
            # For non-simulator providers, use provided data
            alert = data

        logger.info(f"🧪 Test alert requested: {alert_type}")

        # Process through AI
        ai_analysis = ai_provider.analyze_alert(alert)

        # Send notification
        success = messaging_provider.send_message(alert, ai_analysis)

        return jsonify({
            'status': 'success' if success else 'partial_success',
            'alert_sent': success,
            'alert_data': alert,
            'ai_analysis': ai_analysis
        }), 200

    except Exception as e:
        logger.error(f"Test alert failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint - service information"""
    return jsonify({
        'service': 'Juniper AI Alert System',
        'version': '1.0.0',
        'status': 'running',
        'providers': {
            'ai': ai_provider.get_provider_name(),
            'messaging': messaging_provider.get_provider_name(),
            'monitoring': monitoring_provider.get_provider_name()
        },
        'endpoints': {
            'health': '/health',
            'webhook': '/webhook/zabbix',
            'test': '/test/alert (POST)'
        }
    }), 200


# ══════════════════════════════════════════════════════════════════════════════
# APPLICATION ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    logger.info(f"Starting Flask server on {settings.flask_host}:{settings.flask_port}")
    logger.info(f"Debug mode: {settings.flask_debug}")

    app.run(
        host=settings.flask_host,
        port=settings.flask_port,
        debug=settings.flask_debug
    )
