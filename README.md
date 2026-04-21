# 🚀 Juniper AI Alert System

**AI-Powered Network Monitoring with Flexible Provider Architecture**

Automatically analyze Juniper network alerts with AI and receive intelligent notifications on Telegram or WhatsApp.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Provider Setup](#-provider-setup)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Production Deployment](#-production-deployment)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

### 🔄 Flexible Provider System
- **AI Providers**: Ollama (local, free) or Claude (cloud, production)
- **Messaging**: Telegram (free) or Twilio WhatsApp (production)
- **Monitoring**: Zabbix (production) or Simulator (testing)
- **Easy Switching**: Change providers with a single environment variable

### 🤖 Intelligent Analysis
- AI-powered root cause analysis
- Impact assessment
- Actionable recommendations
- Juniper-specific expertise

### 📱 Multi-Channel Notifications
- Telegram Bot (free, instant)
- WhatsApp via Twilio (production-ready)
- Formatted alerts with emoji indicators

### 🔐 Security First
- HMAC webhook authentication
- Environment-based secrets
- IP whitelisting support
- Rate limiting ready

---

## 🏗️ Architecture

```
┌─────────────────┐      SNMP       ┌─────────────────┐
│ Juniper Device  │ ◄──────────────► │ Zabbix Server   │
│ (Router/Switch) │                  │ (Monitoring)    │
└─────────────────┘                  └────────┬────────┘
                                              │
                                              │ Webhook
                                              │ (HTTP POST)
                                              ▼
                                     ┌────────────────────┐
                                     │  Flask Webhook     │
                                     │  Receiver          │
                                     └─────────┬──────────┘
                                               │
                        ┌──────────────────────┼──────────────────────┐
                        │                      │                      │
                        ▼                      ▼                      ▼
              ┌──────────────────┐   ┌──────────────────┐  ┌──────────────────┐
              │ Monitoring       │   │ AI Provider      │  │ Messaging        │
              │ Provider         │   │ (Ollama/Claude)  │  │ Provider         │
              │ (Zabbix)         │   │                  │  │ (Telegram/Twilio)│
              └──────────────────┘   └──────────────────┘  └──────────────────┘
                                               │                      │
                                               │  AI Analysis         │
                                               └──────────┬───────────┘
                                                          │
                                                          ▼
                                                  ┌──────────────────┐
                                                  │ Notification     │
                                                  │ (Telegram/       │
                                                  │  WhatsApp)       │
                                                  └──────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Zabbix server (for production) or use simulator mode
- Ollama installed (for local AI) OR Claude API key
- Telegram account OR Twilio account

### 1. Clone the Repository

```bash
git clone https://github.com/sanketpawar007/zabix-alert-automation.git
cd zabix-alert-automation
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Generate webhook secret
python3 scripts/generate_secret.py

# Edit .env with your settings
nano .env
```

### 5. Set Up Telegram Bot (Recommended for Development)

```bash
# 1. Create bot with @BotFather on Telegram
# 2. Get your chat ID
python3 scripts/setup_telegram.py YOUR_BOT_TOKEN

# 3. Add the chat ID to your .env file
```

### 6. Install and Run Ollama (Local AI)

```bash
# Install Ollama from https://ollama.ai
# Then pull the model
ollama pull llama3.2

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### 7. Start the Application

```bash
python3 app.py
```

The service will start on `http://localhost:5001`

### 8. Test the System

```bash
# Send a test alert
./scripts/test_alert.sh interface_down

# Or use curl
curl -X POST http://localhost:5001/test/alert \
  -H "Content-Type: application/json" \
  -d '{"type": "interface_down"}'
```

Check your Telegram for the notification! 🎉

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROVIDER_AI` | AI provider: `ollama` or `claude` | `ollama` | Yes |
| `PROVIDER_MESSAGING` | Messaging: `telegram` or `twilio` | `telegram` | Yes |
| `PROVIDER_MONITORING` | Monitoring: `zabbix` or `simulator` | `zabbix` | Yes |
| `WEBHOOK_SECRET` | Secret for webhook authentication | - | Yes (except simulator) |
| `MIN_SEVERITY` | Minimum alert severity to process | `High` | No |

### Switching Providers

Simply change the provider variables in `.env`:

```bash
# Development setup (free)
PROVIDER_AI=ollama
PROVIDER_MESSAGING=telegram
PROVIDER_MONITORING=simulator

# Production setup
PROVIDER_AI=claude
PROVIDER_MESSAGING=twilio
PROVIDER_MONITORING=zabbix
```

---

## 🔧 Provider Setup

### Ollama (AI - Local & Free)

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2  # or llama2, mistral, etc.

# Configure in .env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Claude AI (AI - Production)

```bash
# Get API key from https://console.anthropic.com
# Configure in .env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Install the client
pip install anthropic
```

### Telegram (Messaging - Free)

1. **Create Bot**:
   - Open Telegram
   - Search for `@BotFather`
   - Send `/newbot` and follow instructions
   - Copy the bot token

2. **Get Chat ID**:
   ```bash
   python3 scripts/setup_telegram.py YOUR_BOT_TOKEN
   ```

3. **Configure**:
   ```bash
   TELEGRAM_BOT_TOKEN=1234567890:ABCdef...
   TELEGRAM_CHAT_IDS=123456789
   ```

### Twilio WhatsApp (Messaging - Production)

1. Create account at https://twilio.com
2. Set up WhatsApp sandbox or get approved number
3. Configure in `.env`:
   ```bash
   TWILIO_ACCOUNT_SID=ACxxxxx...
   TWILIO_AUTH_TOKEN=xxxxx...
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   WHATSAPP_RECIPIENTS=whatsapp:+1234567890
   ```

---

## 🧪 Testing

### Test Alert Types

```bash
# Interface down alert
./scripts/test_alert.sh interface_down

# High CPU alert
./scripts/test_alert.sh high_cpu

# High memory alert
./scripts/test_alert.sh memory_high

# Resolved alert
./scripts/test_alert.sh resolved
```

### Health Check

```bash
curl http://localhost:5001/health
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information |
| `/health` | GET | Health check with provider status |
| `/webhook/zabbix` | POST | Main webhook endpoint |
| `/test/alert` | POST | Send test alert |

---

## 🚀 Production Deployment

### Deploy to VM

```bash
# SSH to your VM
ssh -i /path/to/key.pem ubuntu@YOUR_VM_IP

# Clone repository
git clone https://github.com/sanketpawar007/zabix-alert-automation.git
cd zabix-alert-automation

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env for production
cp .env.example .env
nano .env  # Update with production settings
```

### Run with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn --workers 4 \
         --bind 127.0.0.1:5001 \
         --timeout 60 \
         --access-logfile logs/access.log \
         app:app
```

### Systemd Service

Create `/etc/systemd/system/alert-service.service`:

```ini
[Unit]
Description=Juniper AI Alert Service
After=network-online.target

[Service]
User=YOUR_USER
WorkingDirectory=/path/to/zabix-alert-automation
EnvironmentFile=/path/to/zabix-alert-automation/.env
ExecStart=/path/to/zabix-alert-automation/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:5001 \
    --timeout 60 \
    app:app
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable alert-service
sudo systemctl start alert-service
sudo systemctl status alert-service
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /webhook/zabbix {
        # Whitelist Zabbix server IP
        allow YOUR_ZABBIX_IP;
        deny all;

        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://127.0.0.1:5001;
    }
}
```

---

## 🔧 Zabbix Configuration

### 1. Create Webhook Media Type

**Administration → Media Types → Create media type**

- **Name**: AI WhatsApp Alerts
- **Type**: Webhook
- **Parameters**:
  - `host` = `{HOST.NAME}`
  - `hostip` = `{HOST.IP}`
  - `name` = `{EVENT.NAME}`
  - `severity` = `{EVENT.SEVERITY}`
  - `status` = `{EVENT.STATUS}`
  - `value` = `{ITEM.VALUE}`
  - `trigger` = `{TRIGGER.NAME}`
  - `eventid` = `{EVENT.ID}`
  - `time` = `{EVENT.DATE} {EVENT.TIME}`

- **Script**:
```javascript
var params = JSON.parse(value);
var req = new HttpRequest();

req.addHeader('Content-Type: application/json');
req.addHeader('X-Webhook-Secret: YOUR_WEBHOOK_SECRET');

var url = 'http://YOUR_SERVER_IP/webhook/zabbix';
var response = req.post(url, JSON.stringify(params));

if (req.getStatus() !== 200) {
    throw 'Alert delivery failed. HTTP status: ' + req.getStatus();
}

return 'Alert sent: ' + response;
```

### 2. Create Action

**Configuration → Actions → Trigger actions → Create action**

- **Name**: Send AI Alerts
- **Conditions**:
  - Trigger severity ≥ High
  - Host group = Your Juniper group
- **Operations**:
  - Send to Users: Your admin user
  - Send only to: AI WhatsApp Alerts

---

## 🐛 Troubleshooting

### Ollama Not Responding

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve

# Check logs
journalctl -u ollama -f
```

### Telegram Not Receiving Messages

```bash
# Verify bot token
python3 scripts/setup_telegram.py YOUR_BOT_TOKEN

# Check if bot is blocked
# Unblock the bot in Telegram and send /start
```

### Webhook Authentication Failed

```bash
# Regenerate secret
python3 scripts/generate_secret.py

# Update both .env and Zabbix webhook script
```

### Check Logs

```bash
# Application logs
tail -f logs/alert-service.log

# Systemd logs
sudo journalctl -u alert-service -f
```

---

## 📁 Project Structure

```
zabix-alert-automation/
├── app.py                      # Main Flask application
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration manager
├── providers/
│   ├── ai/
│   │   ├── base.py             # AI provider interface
│   │   ├── ollama.py           # Ollama implementation
│   │   └── claude.py           # Claude implementation
│   ├── messaging/
│   │   ├── base.py             # Messaging provider interface
│   │   ├── telegram.py         # Telegram implementation
│   │   └── twilio_whatsapp.py  # Twilio implementation
│   └── monitoring/
│       ├── base.py             # Monitoring provider interface
│       ├── zabbix.py           # Zabbix webhook handler
│       └── simulator.py        # Development simulator
├── scripts/
│   ├── test_alert.sh           # Test alert sender
│   ├── setup_telegram.py       # Telegram setup helper
│   └── generate_secret.py      # Secret generator
├── .env.example                # Example configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Original documentation and architecture design
- Anthropic Claude for AI capabilities
- Ollama for local LLM hosting
- Zabbix for network monitoring
- Telegram for free messaging platform

---

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/sanketpawar007/zabix-alert-automation/issues
- Documentation: See docs/ folder for detailed guides

---

**Built with ❤️ for network engineers and system administrators**
