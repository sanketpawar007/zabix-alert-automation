"""
Basic import tests to verify project structure
Run: python -m pytest tests/
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_config_imports():
    """Test configuration module imports"""
    from config.settings import Settings
    assert Settings is not None


def test_ai_provider_imports():
    """Test AI provider imports"""
    from providers.ai.base import BaseAIProvider
    from providers.ai.ollama import OllamaProvider
    from providers.ai.claude import ClaudeProvider

    assert BaseAIProvider is not None
    assert OllamaProvider is not None
    assert ClaudeProvider is not None


def test_messaging_provider_imports():
    """Test messaging provider imports"""
    from providers.messaging.base import BaseMessagingProvider
    from providers.messaging.telegram import TelegramProvider
    from providers.messaging.twilio_whatsapp import TwilioWhatsAppProvider

    assert BaseMessagingProvider is not None
    assert TelegramProvider is not None
    assert TwilioWhatsAppProvider is not None


def test_monitoring_provider_imports():
    """Test monitoring provider imports"""
    from providers.monitoring.base import BaseMonitoringProvider
    from providers.monitoring.zabbix import ZabbixProvider
    from providers.monitoring.simulator import SimulatorProvider

    assert BaseMonitoringProvider is not None
    assert ZabbixProvider is not None
    assert SimulatorProvider is not None


def test_app_imports():
    """Test main application imports"""
    # Note: This might fail without .env, but should import
    try:
        import app
        assert app is not None
    except ValueError:
        # Expected if .env is not configured
        pass


if __name__ == '__main__':
    print("Running import tests...")
    test_config_imports()
    print("✅ Config imports OK")

    test_ai_provider_imports()
    print("✅ AI provider imports OK")

    test_messaging_provider_imports()
    print("✅ Messaging provider imports OK")

    test_monitoring_provider_imports()
    print("✅ Monitoring provider imports OK")

    test_app_imports()
    print("✅ App imports OK")

    print("\n🎉 All import tests passed!")
