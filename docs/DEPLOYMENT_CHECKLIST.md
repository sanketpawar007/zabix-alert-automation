# ✅ Production Deployment Checklist

## Complete Implementation Checklist for Management

**Project:** Juniper AI Alert System
**Estimated Time:** 2-3 days
**Estimated Cost:** $0 (with Ollama + Teams/Email)

---

## Phase 1: Decision & Planning (Day 1 - Morning)

### Management Decisions

- [ ] **Read documentation**
  - [ ] Executive Summary (`docs/EXECUTIVE_SUMMARY.md`)
  - [ ] Production Requirements (`docs/PRODUCTION_REQUIREMENTS.md`)

- [ ] **Choose messaging platform**
  - [ ] Option A: Microsoft Teams (recommended)
  - [ ] Option B: Email/SMTP
  - [ ] Option C: Keep Telegram (not recommended for production)

- [ ] **Choose AI provider**
  - [ ] Option A: Ollama (local, free, private) - recommended
  - [ ] Option B: Claude AI (cloud, $20-50/mo, better quality)

- [ ] **Approve VM provisioning** (if new VM needed)
  - [ ] Review VM requirements (`docs/VM_REQUIREMENTS.md`)
  - [ ] Assign to infrastructure team

- [ ] **Approve network changes**
  - [ ] Firewall rule: Zabbix → VM
  - [ ] Assign to network team

---

## Phase 2: Infrastructure Setup (Day 1 - Afternoon)

### VM Provisioning (If New VM Needed)

- [ ] **Infrastructure team provisions VM**
  - [ ] Ubuntu 22.04 LTS installed
  - [ ] 4 vCPU, 8 GB RAM, 40 GB disk
  - [ ] Static IP assigned
  - [ ] Hostname configured
  - [ ] SSH access configured
  - [ ] sudo privileges for deployment user

- [ ] **Network configuration**
  - [ ] VM can reach Zabbix server (ping test)
  - [ ] Zabbix can reach VM (ping test)
  - [ ] DNS resolution working
  - [ ] NTP synchronized

- [ ] **Firewall rules**
  - [ ] Allow: Zabbix IP → VM IP (port 80)
  - [ ] Allow: Admin IPs → VM IP (port 22)
  - [ ] Allow: VM → SMTP/Teams (outbound)

**Verification:**
```bash
# From Zabbix server
ping VM_IP

# From VM
ping ZABBIX_IP
ping smtp.yourcompany.com  # if using email
curl https://outlook.office.com  # if using Teams
```

---

## Phase 3: Application Deployment (Day 1 - Evening / Day 2 - Morning)

### Deploy Application

- [ ] **SSH to VM**
  ```bash
  ssh ubuntu@VM_IP
  ```

- [ ] **Install system packages**
  ```bash
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y python3 python3-pip python3-venv git curl nginx
  ```

- [ ] **Install Ollama**
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ollama pull llama3.2
  ```

- [ ] **Clone repository**
  ```bash
  cd ~
  git clone https://github.com/sanketpawar007/zabix-alert-automation.git
  cd zabix-alert-automation
  ```

- [ ] **Setup Python environment**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

### Configure Application

- [ ] **Get messaging credentials**
  - **If Teams:**
    - [ ] Get Teams webhook URL from channel
    - [ ] Document: `docs/PRODUCTION_REQUIREMENTS.md` (How to get webhook)
  - **If Email:**
    - [ ] Get SMTP server details from IT
    - [ ] Get SMTP username/password
    - [ ] Get recipient email addresses

- [ ] **Create .env configuration**
  ```bash
  cp .env.example .env
  nano .env
  ```

- [ ] **Configure .env file**
  - [ ] Set `PROVIDER_AI=ollama` (or claude)
  - [ ] Set `PROVIDER_MESSAGING=teams` (or email)
  - [ ] Set `PROVIDER_MONITORING=zabbix`
  - [ ] Add Teams webhook URL OR SMTP details
  - [ ] Generate and add WEBHOOK_SECRET
  - [ ] Set MIN_SEVERITY (High recommended)
  - [ ] Review all settings

- [ ] **Generate webhook secret**
  ```bash
  python3 scripts/generate_secret.py
  # Copy output to .env WEBHOOK_SECRET
  # SAVE THIS - needed for Zabbix configuration!
  ```

- [ ] **Test configuration**
  ```bash
  python3 app.py
  # Should start without errors
  # Press Ctrl+C to stop
  ```

### Deploy as System Service

- [ ] **Create systemd service**
  ```bash
  sudo cp deployment/alert-service.service /etc/systemd/system/
  # Or manually create from docs/DEPLOYMENT.md
  ```

- [ ] **Enable and start service**
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable alert-service
  sudo systemctl start alert-service
  ```

- [ ] **Verify service is running**
  ```bash
  sudo systemctl status alert-service
  curl http://localhost:5001/health
  ```

### Setup Nginx Reverse Proxy

- [ ] **Configure Nginx**
  ```bash
  sudo nano /etc/nginx/sites-available/alert-service
  # Copy config from docs/DEPLOYMENT.md
  # UPDATE: server_name, Zabbix IP
  ```

- [ ] **Enable site**
  ```bash
  sudo ln -s /etc/nginx/sites-available/alert-service /etc/nginx/sites-enabled/
  sudo nginx -t
  sudo systemctl reload nginx
  ```

- [ ] **Test Nginx**
  ```bash
  curl http://VM_IP/health
  ```

---

## Phase 4: Zabbix Integration (Day 2 - Afternoon)

### Juniper Device Check

- [ ] **Verify Juniper SNMP status**
  - [ ] SSH to Zabbix server
  - [ ] Run: `snmpwalk -v 2c -c COMMUNITY JUNIPER_IP system`
  - [ ] If works: ✅ No changes needed
  - [ ] If fails: ⚠️ See `docs/JUNIPER_DEVICE_SETUP.md`

- [ ] **If SNMP needs configuration**
  - [ ] Provide `docs/JUNIPER_DEVICE_SETUP.md` to network team
  - [ ] Network team configures SNMP on devices
  - [ ] Test SNMP from Zabbix server
  - [ ] Verify data appears in Zabbix

### Zabbix Webhook Configuration

- [ ] **Access Zabbix web UI**
  - [ ] Log in as administrator

- [ ] **Create Media Type**
  - [ ] Go to: Administration → Media Types → Create
  - [ ] Name: `Juniper AI Alerts`
  - [ ] Type: `Webhook`
  - [ ] Add parameters (see `docs/PRODUCTION_REQUIREMENTS.md`)
  - [ ] Add webhook script:
    - [ ] Update URL: `http://VM_IP/webhook/zabbix`
    - [ ] Update secret: Use generated WEBHOOK_SECRET
  - [ ] Save

- [ ] **Configure User Media**
  - [ ] Go to: Administration → Users
  - [ ] Select admin user → Media tab
  - [ ] Add media:
    - [ ] Type: Juniper AI Alerts
    - [ ] When active: 1-7, 00:00-24:00
    - [ ] Severity: Check all
  - [ ] Update

- [ ] **Create Action**
  - [ ] Go to: Configuration → Actions → Trigger actions
  - [ ] Create action: `Send Juniper AI Alerts`
  - [ ] Conditions:
    - [ ] Trigger severity ≥ High
    - [ ] Host group = Juniper devices
  - [ ] Operations:
    - [ ] Send to user: admin
    - [ ] Send only to: Juniper AI Alerts
  - [ ] Recovery operations: Same as above
  - [ ] Save

---

## Phase 5: Testing (Day 2 - Evening)

### Unit Tests

- [ ] **Test health endpoint**
  ```bash
  curl http://VM_IP/health
  # Should return: {"status":"healthy"...}
  ```

- [ ] **Test AI provider**
  ```bash
  # Check Ollama
  curl http://localhost:11434/api/tags
  # Should list llama3.2 model
  ```

- [ ] **Test messaging provider**
  - **If Teams:**
    ```bash
    # Send test message to Teams webhook
    curl -X POST TEAMS_WEBHOOK_URL \
      -H "Content-Type: application/json" \
      -d '{"text":"Test from Juniper AI Alert System"}'
    # Check Teams channel for message
    ```
  - **If Email:**
    ```bash
    # Check SMTP connectivity
    telnet SMTP_SERVER SMTP_PORT
    # Should connect
    ```

### Integration Tests

- [ ] **Test from Zabbix server**
  ```bash
  # SSH to Zabbix server
  curl -X POST http://VM_IP/webhook/zabbix \
    -H "Content-Type: application/json" \
    -H "X-Webhook-Secret: YOUR_WEBHOOK_SECRET" \
    -d '{
      "host":"test-device",
      "hostip":"192.168.1.1",
      "name":"Test Alert",
      "severity":"High",
      "status":"PROBLEM",
      "value":"test",
      "trigger":"Test Trigger",
      "eventid":"99999",
      "time":"'$(date '+%Y-%m-%d %H:%M:%S')'"
    }'
  ```

- [ ] **Verify alert received**
  - [ ] Check Teams channel OR Email inbox
  - [ ] Verify message has AI analysis
  - [ ] Verify formatting is correct

- [ ] **Check application logs**
  ```bash
  tail -50 /home/ubuntu/zabix-alert-automation/logs/alert-service.log
  # Should show: Alert received → AI analysis → Message sent
  ```

### Production Test with Real Alert

- [ ] **Trigger test alert in Zabbix**
  - [ ] Manually trigger a test alert
  - [ ] Or wait for natural alert
  - [ ] Verify arrives in Teams/Email within seconds

- [ ] **Verify alert quality**
  - [ ] AI analysis makes sense
  - [ ] Recommendations are relevant
  - [ ] Formatting is clean
  - [ ] All data fields present

---

## Phase 6: Monitoring & Documentation (Day 3)

### Monitoring Setup

- [ ] **Add VM to monitoring**
  - [ ] CPU usage
  - [ ] RAM usage
  - [ ] Disk space
  - [ ] Service status

- [ ] **Setup alerts for VM**
  - [ ] Alert if service stops
  - [ ] Alert if disk >80%
  - [ ] Alert if RAM >90%

- [ ] **Configure log rotation**
  ```bash
  sudo nano /etc/logrotate.d/alert-service
  # Add rotation rules
  ```

### Backup & DR

- [ ] **Backup .env file**
  ```bash
  # Secure backup location
  sudo cp /home/ubuntu/zabix-alert-automation/.env /backup/location/
  ```

- [ ] **Document in CMDB**
  - [ ] VM details
  - [ ] IP address
  - [ ] Purpose
  - [ ] Owner
  - [ ] Backup schedule

- [ ] **Create runbook**
  - [ ] How to restart service
  - [ ] How to check logs
  - [ ] How to update configuration
  - [ ] Emergency contacts

### Team Training

- [ ] **Train team on new alerts**
  - [ ] Alert format explanation
  - [ ] How to interpret AI analysis
  - [ ] When to escalate
  - [ ] How to acknowledge

- [ ] **Share documentation**
  - [ ] README.md (overview)
  - [ ] Troubleshooting guide
  - [ ] Configuration reference

---

## Phase 7: Go-Live (Day 3)

### Final Checks

- [ ] **Verify all components**
  - [ ] VM running: `systemctl status alert-service`
  - [ ] Nginx running: `systemctl status nginx`
  - [ ] Ollama running: `systemctl status ollama`
  - [ ] Firewall rules active: `sudo ufw status`

- [ ] **Performance check**
  - [ ] CPU usage normal (<50%)
  - [ ] RAM usage normal (<70%)
  - [ ] Disk space adequate (>50% free)
  - [ ] No errors in logs

- [ ] **Security audit**
  - [ ] Webhook secret is strong
  - [ ] Firewall rules correct
  - [ ] SSH keys only (no passwords)
  - [ ] Service runs as non-root
  - [ ] Nginx IP whitelist correct

### Enable Production

- [ ] **Enable Zabbix action**
  - [ ] Ensure action is enabled
  - [ ] Verify conditions are correct
  - [ ] Set to active

- [ ] **Monitor first 24 hours**
  - [ ] Watch for alerts
  - [ ] Check delivery success
  - [ ] Review AI analysis quality
  - [ ] Note any issues

- [ ] **Announce to team**
  - [ ] Email announcement
  - [ ] Training session
  - [ ] Share documentation
  - [ ] Collect feedback

---

## Post-Deployment

### Week 1 Review

- [ ] **Review metrics**
  - [ ] Number of alerts processed
  - [ ] AI analysis quality
  - [ ] Delivery success rate
  - [ ] Response time

- [ ] **Tune if needed**
  - [ ] Adjust severity filters
  - [ ] Update alert templates
  - [ ] Optimize AI prompts
  - [ ] Refine alert conditions

### Month 1 Review

- [ ] **Performance review**
  - [ ] VM resource usage
  - [ ] Alert volume trends
  - [ ] Team feedback
  - [ ] Incident response improvement

- [ ] **Consider upgrades**
  - [ ] Ollama → Claude AI (if better analysis needed)
  - [ ] Add second VM (if high availability needed)
  - [ ] Add SSL certificate
  - [ ] Integrate with ticketing system

---

## Success Criteria

### Technical Success

- ✅ Service uptime >99%
- ✅ All alerts delivered <10 seconds
- ✅ AI analysis accuracy >90%
- ✅ Zero security incidents
- ✅ Zero data loss

### Business Success

- ✅ Faster incident response time
- ✅ Team satisfaction with alerts
- ✅ Management approval
- ✅ Under budget ($0/month target)
- ✅ Compliance requirements met

---

## Rollback Plan

If issues occur:

- [ ] **Stop service**
  ```bash
  sudo systemctl stop alert-service
  ```

- [ ] **Disable Zabbix action**
  - Go to Zabbix → Actions → Disable action

- [ ] **Revert to previous alerting**
  - Enable old email alerts
  - Document issues

- [ ] **Troubleshoot offline**
  - Review logs
  - Fix issues
  - Test again before re-enabling

---

## Sign-Off

| Role | Name | Sign | Date |
|------|------|------|------|
| **Project Lead** | | | |
| **Senior Network Admin** | | | |
| **Infrastructure Team** | | | |
| **Network Team** | | | |
| **Zabbix Admin** | | | |
| **Security Team** | | | |

---

## Appendix: Quick Reference

### Important Files

| File | Purpose |
|------|---------|
| `/home/ubuntu/zabix-alert-automation/.env` | Configuration (secrets) |
| `/home/ubuntu/zabix-alert-automation/logs/alert-service.log` | Application logs |
| `/etc/systemd/system/alert-service.service` | Service definition |
| `/etc/nginx/sites-available/alert-service` | Nginx config |

### Important Commands

```bash
# Restart service
sudo systemctl restart alert-service

# View logs
tail -f /home/ubuntu/zabix-alert-automation/logs/alert-service.log

# Check health
curl http://localhost:5001/health

# Update code
cd /home/ubuntu/zabix-alert-automation
git pull
sudo systemctl restart alert-service
```

### Support Contacts

| Issue | Contact | Email/Phone |
|-------|---------|-------------|
| Application issues | You | your-email@company.com |
| VM issues | Infrastructure team | infra@company.com |
| Network issues | Network team | network@company.com |
| Zabbix issues | Zabbix admin | zabbix@company.com |

---

**Checklist Version:** 1.0
**Last Updated:** 2026-04-21
**Status:** Ready for deployment
