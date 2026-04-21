# 🚀 Quick Start Guide

Get the Juniper AI Alert System running in under 10 minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Git installed
- [ ] Telegram account (for free notifications)
- [ ] Ollama installed (for free local AI)

---

## Step-by-Step Setup

### 1. Install Ollama (Local AI)

```bash
# macOS/Linux
curl https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai

# Pull the model
ollama pull llama3.2
```

### 2. Clone Repository

```bash
git clone https://github.com/sanketpawar007/zabix-alert-automation.git
cd zabix-alert-automation
```

### 3. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Choose a name and username for your bot
4. **Copy the bot token** (looks like: `1234567890:ABCdef...`)

### 5. Get Your Telegram Chat ID

```bash
# Method 1: Use our helper script
python3 scripts/setup_telegram.py YOUR_BOT_TOKEN

# Method 2: Manual
# 1. Start a chat with your bot in Telegram
# 2. Send any message (e.g., "hello")
# 3. Visit: https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
# 4. Find your chat ID in the response
```

### 6. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Generate webhook secret
python3 scripts/generate_secret.py
# Copy the generated secret

# Edit configuration
nano .env  # or use your favorite editor
```

**Minimal .env configuration:**

```bash
# Provider selection
PROVIDER_AI=ollama
PROVIDER_MESSAGING=telegram
PROVIDER_MONITORING=simulator  # Use simulator for testing

# Telegram settings
TELEGRAM_BOT_TOKEN=paste-your-bot-token-here
TELEGRAM_CHAT_IDS=paste-your-chat-id-here

# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Webhook secret (from step above)
WEBHOOK_SECRET=paste-generated-secret-here

# Keep other defaults
MIN_SEVERITY=High
FLASK_HOST=127.0.0.1
FLASK_PORT=5001
```

### 7. Start the Application

```bash
# Make sure Ollama is running
ollama serve  # In a separate terminal

# Start the alert service
python3 app.py
```

You should see:

```
═══════════════════════════════════════════════════════════════════
🚀 Juniper AI Alert System Starting
═══════════════════════════════════════════════════════════════════
AI Provider:         Ollama
Messaging Provider:  Telegram
Monitoring Provider: Simulator
═══════════════════════════════════════════════════════════════════
 * Running on http://127.0.0.1:5001
```

### 8. Test the System

Open a **new terminal** and run:

```bash
# Test with default interface down alert
./scripts/test_alert.sh

# Or test different alert types
./scripts/test_alert.sh high_cpu
./scripts/test_alert.sh memory_high
./scripts/test_alert.sh resolved
```

**Check your Telegram!** You should receive a formatted alert message with AI analysis! 🎉

---

## 🎯 What You've Built

- ✅ Local AI analysis (Ollama) - completely free
- ✅ Telegram notifications - completely free
- ✅ Flexible architecture - easy to switch to production tools
- ✅ Test mode - can test without real Zabbix

---

## 🔄 Next Steps

### Switch to Production Zabbix

1. Update `.env`:
   ```bash
   PROVIDER_MONITORING=zabbix
   ```

2. Configure Zabbix webhook (see README.md "Zabbix Configuration" section)

3. Restart the service

### Switch to Claude AI (Production)

1. Get Claude API key from https://console.anthropic.com
2. Install Claude client:
   ```bash
   pip install anthropic
   ```
3. Update `.env`:
   ```bash
   PROVIDER_AI=claude
   ANTHROPIC_API_KEY=your-api-key-here
   ```

### Switch to WhatsApp (Production)

1. Create Twilio account at https://twilio.com
2. Set up WhatsApp
3. Install Twilio client:
   ```bash
   pip install twilio
   ```
4. Update `.env`:
   ```bash
   PROVIDER_MESSAGING=twilio
   TWILIO_ACCOUNT_SID=your-sid
   TWILIO_AUTH_TOKEN=your-token
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   WHATSAPP_RECIPIENTS=whatsapp:+1234567890
   ```

---

## 🐛 Troubleshooting

### Ollama Connection Error

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

### Telegram Not Receiving Messages

- Make sure you sent a message to your bot first
- Verify bot token and chat ID are correct
- Check the bot isn't blocked

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Health Check

```bash
# Check service status
curl http://localhost:5001/health

# Should return healthy status with provider info
```

---

## 📚 Further Reading

- [Full README](../README.md) - Complete documentation
- [Deployment Guide](DEPLOYMENT.md) - Production deployment
- [Configuration Reference](.env.example) - All environment variables

---

**Need help?** Open an issue on GitHub!
