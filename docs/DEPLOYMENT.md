# 🚀 Production Deployment Guide

Complete guide for deploying to your Oracle VM and production environment.

---

## 📋 Deployment Checklist

- [ ] VM access verified
- [ ] Production credentials ready
- [ ] Ollama installed on VM
- [ ] Telegram bot created
- [ ] Zabbix server accessible
- [ ] Git repository access
- [ ] Firewall rules planned

---

## 🖥️ VM Deployment

### Connect to Your VM

```bash
ssh -i /Users/sanketpawar/Desktop/Oracle-VM-Keys/openclaw-vm/openclaw.pem ubuntu@168.110.54.2
```

### Initial Server Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv git curl nginx

# Install Ollama on VM
curl https://ollama.ai/install.sh | sh

# Pull the AI model
ollama pull llama3.2

# Verify Ollama is running
systemctl status ollama
```

### Deploy Application

```bash
# Navigate to deployment directory
cd /home/ubuntu

# Clone repository
git clone https://github.com/sanketpawar007/zabix-alert-automation.git
cd zabix-alert-automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Gunicorn for production
pip install gunicorn
```

### Configure Environment

```bash
# Copy example config
cp .env.example .env

# Generate webhook secret
python3 scripts/generate_secret.py
# SAVE THIS SECRET - you'll need it for Zabbix configuration

# Edit configuration
nano .env
```

**Production .env example:**

```bash
# Providers
PROVIDER_AI=ollama
PROVIDER_MESSAGING=telegram
PROVIDER_MONITORING=zabbix

# Telegram (from your bot setup)
TELEGRAM_BOT_TOKEN=your-production-bot-token
TELEGRAM_CHAT_IDS=your-production-chat-ids

# Ollama (local on VM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Security (generated secret)
WEBHOOK_SECRET=your-generated-secret-here

# Production settings
MIN_SEVERITY=High
FLASK_HOST=127.0.0.1
FLASK_PORT=5001
FLASK_DEBUG=False
LOG_LEVEL=INFO
```

### Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/alert-service.service
```

Paste this configuration:

```ini
[Unit]
Description=Juniper AI Alert Service
Documentation=https://github.com/sanketpawar007/zabix-alert-automation
After=network-online.target ollama.service
Wants=network-online.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/zabix-alert-automation
EnvironmentFile=/home/ubuntu/zabix-alert-automation/.env

ExecStart=/home/ubuntu/zabix-alert-automation/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:5001 \
    --timeout 60 \
    --access-logfile /home/ubuntu/zabix-alert-automation/logs/access.log \
    --error-logfile /home/ubuntu/zabix-alert-automation/logs/error.log \
    --log-level info \
    app:app

Restart=on-failure
RestartSec=5s
StartLimitIntervalSec=60
StartLimitBurst=3

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/ubuntu/zabix-alert-automation/logs

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Create logs directory
mkdir -p /home/ubuntu/zabix-alert-automation/logs

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable alert-service

# Start service
sudo systemctl start alert-service

# Check status
sudo systemctl status alert-service

# View logs
sudo journalctl -u alert-service -f
```

---

## 🔒 Nginx Configuration

### Install and Configure Nginx

```bash
# Install Nginx
sudo apt install nginx -y

# Create site configuration
sudo nano /etc/nginx/sites-available/alert-service
```

**Nginx configuration:**

```nginx
# Rate limiting zone
limit_req_zone $binary_remote_addr zone=webhooks:10m rate=30r/m;

server {
    listen 80;
    server_name 168.110.54.2;  # Your VM IP or domain

    # Access logs
    access_log /var/log/nginx/alert-service-access.log;
    error_log /var/log/nginx/alert-service-error.log;

    # Health check endpoint (accessible from anywhere)
    location /health {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 30s;
    }

    # Webhook endpoint (restricted to Zabbix server)
    location /webhook/zabbix {
        # IMPORTANT: Replace with your actual Zabbix server IP
        allow YOUR_ZABBIX_SERVER_IP;
        deny all;

        # Rate limiting
        limit_req zone=webhooks burst=5 nodelay;

        # Request size limit
        client_max_body_size 1m;

        # Proxy to Flask
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Timeouts
        proxy_connect_timeout 10s;
        proxy_read_timeout 90s;
        proxy_send_timeout 10s;
    }

    # Block everything else
    location / {
        return 404;
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
```

### Enable Nginx Site

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/alert-service /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Verify Nginx is running
sudo systemctl status nginx
```

---

## 🔥 Firewall Configuration

### Configure UFW

```bash
# Install UFW
sudo apt install ufw -y

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (IMPORTANT - don't lock yourself out!)
sudo ufw allow ssh

# Allow HTTP (for Nginx)
sudo ufw allow http

# Allow HTTPS (if you add SSL later)
sudo ufw allow https

# Allow from Zabbix server only (replace with actual IP)
sudo ufw allow from YOUR_ZABBIX_SERVER_IP to any port 80

# Deny direct access to Flask port
sudo ufw deny 5001

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

---

## 🔌 Zabbix Integration

### Configure Zabbix Webhook

1. **Log into Zabbix Web UI**

2. **Create Media Type**:
   - Go to: **Administration → Media Types → Create media type**
   - **Name**: `Juniper AI Alerts`
   - **Type**: `Webhook`

3. **Add Parameters**:

   | Parameter | Value |
   |-----------|-------|
   | host | `{HOST.NAME}` |
   | hostip | `{HOST.IP}` |
   | name | `{EVENT.NAME}` |
   | severity | `{EVENT.SEVERITY}` |
   | status | `{EVENT.STATUS}` |
   | value | `{ITEM.VALUE}` |
   | trigger | `{TRIGGER.NAME}` |
   | eventid | `{EVENT.ID}` |
   | time | `{EVENT.DATE} {EVENT.TIME}` |

4. **Webhook Script**:

```javascript
var params = JSON.parse(value);
var req = new HttpRequest();

// Set headers
req.addHeader('Content-Type: application/json');
req.addHeader('X-Webhook-Secret: YOUR_WEBHOOK_SECRET_HERE');

// Your VM webhook URL
var url = 'http://168.110.54.2/webhook/zabbix';

// Send alert
var response = req.post(url, JSON.stringify(params));

// Check response
if (req.getStatus() !== 200) {
    throw 'Alert delivery failed. HTTP status: ' + req.getStatus();
}

Zabbix.log(4, 'AI alert sent successfully for: ' + params.host);
return 'Alert sent: ' + response;
```

5. **Create User Media**:
   - Go to: **Administration → Users**
   - Select your user → **Media** tab
   - Click **Add**
   - **Type**: Select `Juniper AI Alerts`
   - **Send to**: (leave empty or use email)
   - **When active**: `1-7,00:00-24:00`
   - **Severity**: Check all boxes
   - Click **Add**

6. **Create Action**:
   - Go to: **Configuration → Actions → Trigger actions**
   - Click **Create action**
   - **Name**: `Send Juniper AI Alerts`

   **Conditions tab**:
   - Trigger severity ≥ High
   - Host group = Your Juniper devices group

   **Operations tab**:
   - Click **Add** under Operations
   - **Send to Users**: Select your user
   - **Send only to**: `Juniper AI Alerts`
   - Click **Add**

---

## 🧪 Testing Production Deployment

### 1. Test Service Health

```bash
# From VM
curl http://localhost:5001/health

# From external (if firewall allows)
curl http://168.110.54.2/health
```

### 2. Test Webhook Locally

```bash
# SSH to VM
ssh -i /path/to/key.pem ubuntu@168.110.54.2

# Run test alert
cd zabix-alert-automation
./scripts/test_alert.sh interface_down
```

### 3. Test from Zabbix Server

```bash
# SSH to Zabbix server
# Test webhook endpoint
curl -X POST http://168.110.54.2/webhook/zabbix \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: YOUR_WEBHOOK_SECRET" \
  -d '{
    "host": "test-device",
    "hostip": "192.168.1.1",
    "name": "Test Alert",
    "severity": "High",
    "status": "PROBLEM",
    "value": "test",
    "trigger": "Test Trigger",
    "eventid": "99999",
    "time": "2026-04-21 12:00:00"
  }'
```

### 4. Trigger Real Alert in Zabbix

Create a test trigger in Zabbix and wait for it to fire.

---

## 📊 Monitoring & Maintenance

### View Logs

```bash
# Application logs
tail -f /home/ubuntu/zabix-alert-automation/logs/alert-service.log

# Systemd logs
sudo journalctl -u alert-service -f

# Nginx access logs
sudo tail -f /var/log/nginx/alert-service-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/alert-service-error.log
```

### Service Management

```bash
# Restart service
sudo systemctl restart alert-service

# Stop service
sudo systemctl stop alert-service

# Start service
sudo systemctl start alert-service

# Check status
sudo systemctl status alert-service
```

### Log Rotation

Create `/etc/logrotate.d/alert-service`:

```
/home/ubuntu/zabix-alert-automation/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        sudo systemctl reload alert-service
    endscript
}
```

### Updates

```bash
# Pull latest code
cd /home/ubuntu/zabix-alert-automation
git pull origin main

# Restart service
sudo systemctl restart alert-service
```

---

## 🔄 Switching Providers in Production

### Switch to Claude AI

```bash
# Install Claude client
source venv/bin/activate
pip install anthropic

# Update .env
nano .env
# Change: PROVIDER_AI=claude
# Add: ANTHROPIC_API_KEY=your-key-here

# Restart service
sudo systemctl restart alert-service
```

### Switch to WhatsApp

```bash
# Install Twilio client
source venv/bin/activate
pip install twilio

# Update .env
nano .env
# Change: PROVIDER_MESSAGING=twilio
# Add Twilio credentials

# Restart service
sudo systemctl restart alert-service
```

---

## 🔒 Security Best Practices

1. **Change webhook secret regularly**
2. **Restrict Nginx access to Zabbix IP only**
3. **Enable UFW firewall**
4. **Use HTTPS with SSL certificate** (Let's Encrypt)
5. **Keep logs directory permissions restricted**
6. **Regularly update system packages**
7. **Monitor unauthorized access attempts**

---

## 📞 Support

If you encounter issues:
1. Check logs first
2. Verify all environment variables
3. Test each component individually
4. Review Zabbix action log
5. Open GitHub issue with logs

---

**Deployment complete! Your production system is ready! 🎉**
