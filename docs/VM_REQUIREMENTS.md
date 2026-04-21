# 🖥️ VM Requirements for Production Deployment

## Virtual Machine Specifications

### Minimum Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **CPU** | 2 vCPUs | 4 vCPUs | More CPUs = faster AI analysis |
| **RAM** | 4 GB | 8 GB | Ollama needs ~2-3GB for model |
| **Storage** | 20 GB | 40 GB | OS + Ollama model + logs |
| **Network** | 1 Gbps NIC | 1 Gbps NIC | For webhook communication |

### Our Development VM (Working Configuration)

```
Current VM: 168.110.54.2
CPU: ARM64 architecture (Oracle Cloud)
RAM: Working with current allocation
OS: Ubuntu 22.04 LTS
Status: ✅ Currently running successfully
```

---

## Operating System Requirements

### Supported OS (Tested)

- ✅ **Ubuntu 20.04 LTS** (recommended)
- ✅ **Ubuntu 22.04 LTS** (tested on dev VM)
- ✅ **Debian 11+**
- ✅ **CentOS 8 / Rocky Linux 8+**
- ✅ **RHEL 8+**

### Architecture Support

- ✅ **x86_64 (AMD64)** - Best performance
- ✅ **ARM64 (aarch64)** - Tested (our dev VM)

---

## Software Prerequisites

### Required Packages

```bash
# System utilities
- python3 (version 3.8 or higher)
- python3-pip
- python3-venv
- git
- curl
- nginx (for reverse proxy)

# AI Engine
- ollama (installed separately - ~1.5GB download)

# Monitoring
- systemd (for service management)
```

### Installation Size Breakdown

| Component | Disk Space | RAM Usage |
|-----------|------------|-----------|
| Operating System | ~5 GB | ~500 MB |
| Python + Dependencies | ~500 MB | ~100 MB |
| Ollama Binary | ~500 MB | ~50 MB |
| Ollama Model (llama3.2) | ~2 GB | ~2-3 GB (when running) |
| Application Code | ~10 MB | ~50 MB |
| Logs (monthly) | ~100 MB | N/A |
| **Total** | **~8 GB** | **~3-4 GB** |

**Recommended VM Storage:** 40 GB (to allow for growth and updates)

---

## Network Requirements

### Inbound Access

| Source | Destination | Port | Protocol | Purpose |
|--------|-------------|------|----------|---------|
| Zabbix Server IP | VM IP | 80 | TCP | Webhook delivery (HTTP) |
| Zabbix Server IP | VM IP | 443 | TCP | Webhook delivery (HTTPS - optional) |
| Admin Workstations | VM IP | 22 | TCP | SSH management |

### Outbound Access

| Destination | Port | Protocol | Purpose | Required When |
|-------------|------|----------|---------|---------------|
| Microsoft Teams API | 443 | TCP | Teams notifications | Using Teams provider |
| Internal SMTP Server | 25/587 | TCP | Email notifications | Using Email provider |
| *(No internet needed)* | - | - | Ollama AI analysis | ✅ Fully offline capable |

**Important:** With Ollama + Teams/Email, the VM can run **100% within your network** after initial setup.

### Initial Setup Only (One-time)

| Destination | Port | Purpose | Can Disconnect After |
|-------------|------|---------|---------------------|
| Ubuntu Package Repos | 80/443 | Install system packages | ✅ Yes |
| PyPI (pip) | 443 | Install Python packages | ✅ Yes |
| Ollama CDN | 443 | Download AI model | ✅ Yes |
| GitHub (optional) | 443 | Clone code repository | ✅ Yes |

---

## Firewall Configuration

### UFW (Ubuntu Firewall) Rules

```bash
# Default policies
Default incoming: DENY
Default outgoing: ALLOW

# SSH access (from admin IPs only)
Port 22 → ALLOW from YOUR_ADMIN_IP

# Webhook from Zabbix
Port 80 → ALLOW from ZABBIX_SERVER_IP

# HTTPS (if using SSL)
Port 443 → ALLOW from ZABBIX_SERVER_IP

# Block everything else
All other ports → DENY
```

### Network Firewall (Data Center Level)

If you have network-level firewalls, ensure:

```
✅ Zabbix Server → VM (port 80/443)
✅ VM → Internal SMTP/Teams (outbound HTTPS)
✅ Admin workstations → VM (SSH port 22)
```

---

## High Availability Considerations

### Current Setup (Single VM)

- ✅ Suitable for most environments
- ✅ Systemd auto-restart on failure
- ✅ Zabbix queues alerts if VM down temporarily
- ⚠️ Single point of failure

### Future HA Options (Optional)

If you need high availability:

1. **Active-Passive Setup**
   - 2 VMs with shared configuration
   - Keepalived for IP failover
   - Estimated cost: 2x VM resources

2. **Load Balanced Setup**
   - 2+ VMs behind load balancer
   - Zabbix sends webhooks to LB
   - Better for high alert volume

**Recommendation:** Start with single VM. Add HA later if needed.

---

## Performance Estimates

### Alert Processing Capacity

| Metric | Single VM (4 vCPU, 8GB RAM) |
|--------|------------------------------|
| **Alerts per minute** | ~10-15 alerts |
| **AI analysis time** | 3-10 seconds per alert |
| **Concurrent processing** | 2-4 alerts simultaneously |
| **Daily capacity** | ~5,000-10,000 alerts |

**Typical Usage:** Most networks generate 10-100 alerts/day → VM is over-provisioned

### Scaling Considerations

If you exceed capacity:
- ✅ Add more CPU cores (faster AI analysis)
- ✅ Switch to Claude AI (cloud-based, faster)
- ✅ Add second VM for load balancing

---

## Storage & Log Management

### Disk Usage Growth

| Component | Initial | Monthly Growth | Yearly |
|-----------|---------|----------------|--------|
| Application | 10 MB | 0 MB | 10 MB |
| Ollama Model | 2 GB | 0 MB | 2 GB |
| Alert Logs | 10 MB | 50-100 MB | 600-1200 MB |
| System Logs | 50 MB | 100 MB | 1.2 GB |
| **Total** | **~2 GB** | **~150-200 MB** | **~4 GB** |

### Log Rotation

Configured to:
- Rotate daily
- Keep 30 days
- Compress old logs
- Auto-cleanup after 30 days

**Recommendation:** 40 GB storage provides ~10 years of log capacity

---

## Backup Requirements

### What to Backup

| Item | Frequency | Size | Priority |
|------|-----------|------|----------|
| **`.env` configuration** | After changes | 1 KB | 🔴 Critical |
| **Application code** | After updates | 10 MB | 🟠 High |
| **Alert logs** | Daily | ~2-5 MB/day | 🟡 Medium |
| **Ollama model** | After updates | 2 GB | 🟢 Low (can re-download) |

### Backup Strategy

```bash
# Critical files to backup
/home/ubuntu/zabix-alert-automation/.env
/home/ubuntu/zabix-alert-automation/logs/

# Can be restored from GitHub
/home/ubuntu/zabix-alert-automation/ (code)

# Can be re-downloaded
/home/ubuntu/.ollama/models/
```

**Recommendation:**
- Daily backup of `.env` and logs
- Weekly backup of entire application directory
- Store backups in your standard backup location

---

## Disaster Recovery

### Recovery Time Objective (RTO)

| Scenario | Recovery Time | Steps |
|----------|---------------|-------|
| **Service crash** | < 1 minute | Systemd auto-restarts |
| **VM reboot** | < 5 minutes | Service starts on boot |
| **VM failure** | 30-60 minutes | Deploy to new VM from docs |
| **Total datacenter loss** | 2-4 hours | Rebuild from scratch |

### Recovery Procedure

If VM is lost:

1. **Provision new VM** (20 min)
2. **Install OS packages** (10 min)
3. **Clone from GitHub** (2 min)
4. **Restore .env from backup** (2 min)
5. **Install Ollama + model** (15 min)
6. **Start services** (5 min)

**Total:** ~60 minutes to full recovery

---

## Security Hardening (Recommended)

### OS Level

```bash
✅ Keep Ubuntu updated (monthly)
✅ SSH key-only authentication
✅ Disable root login
✅ Enable UFW firewall
✅ Install fail2ban (SSH protection)
✅ Regular security audits
```

### Application Level

```bash
✅ Run as non-root user (alertbot)
✅ Environment-based secrets (.env)
✅ HMAC webhook authentication
✅ IP whitelisting in Nginx
✅ Rate limiting
✅ TLS/SSL for webhooks (optional)
```

---

## Monitoring the VM

### What to Monitor

| Metric | Threshold | Action |
|--------|-----------|--------|
| **CPU Usage** | > 80% sustained | Consider more CPUs |
| **RAM Usage** | > 90% | Add more RAM |
| **Disk Space** | > 80% | Cleanup old logs |
| **Service Status** | Stopped | Investigate logs |
| **Network Latency** | > 100ms to Zabbix | Check network |

### Monitoring Endpoints

```bash
# Health check (add to your monitoring)
curl http://VM_IP/health

# Expected response
{"status":"healthy","providers":{...}}

# Service status
systemctl status alert-service
```

---

## Cost Estimate

### VM Hosting Options

| Provider | Specs | Monthly Cost | Notes |
|----------|-------|--------------|-------|
| **On-Premises (Physical)** | Varies | $0 | Use existing hardware |
| **VMware vSphere** | 4 vCPU, 8GB | $0 | Use existing VMware license |
| **Hyper-V** | 4 vCPU, 8GB | $0 | Use existing Windows Server |
| **Oracle Cloud (Free Tier)** | 4 vCPU, 24GB ARM | **$0** | Up to 4 ARM instances free |
| **AWS EC2 t3.medium** | 2 vCPU, 4GB | ~$30 | If you need cloud |
| **Azure B2s** | 2 vCPU, 4GB | ~$30 | If you need cloud |

**Current Setup:** Using Oracle Cloud Free Tier (ARM) = **$0/month**

---

## VM Provisioning Checklist

### For Your Infrastructure Team

```
☐ Provision VM with specifications:
  ☐ 4 vCPUs (minimum 2)
  ☐ 8 GB RAM (minimum 4)
  ☐ 40 GB storage (minimum 20)
  ☐ Ubuntu 22.04 LTS
  ☐ Network connectivity to Zabbix server

☐ Network configuration:
  ☐ Static IP address assigned
  ☐ Hostname configured
  ☐ DNS resolution working

☐ Firewall rules:
  ☐ Allow Zabbix Server → VM (port 80)
  ☐ Allow Admin IPs → VM (port 22)
  ☐ Allow VM → Internal SMTP/Teams

☐ Access:
  ☐ SSH access for deployment user
  ☐ sudo privileges for deployment user
  ☐ SSH key-based authentication

☐ Monitoring:
  ☐ Add VM to infrastructure monitoring
  ☐ Set up backup jobs
  ☐ Document in CMDB
```

---

## Questions for Your Senior

**VM Provisioning:**
1. ☐ Can we use an existing VM or need new one?
2. ☐ Preferred hosting platform? (VMware/Hyper-V/Cloud)
3. ☐ What IP address range to use?
4. ☐ Who provisions the VM? (Infrastructure team)

**Network:**
5. ☐ Zabbix server IP address?
6. ☐ Internal SMTP server details (if using email)?
7. ☐ Any proxy servers required for outbound traffic?

**Security:**
8. ☐ Any additional security requirements?
9. ☐ SSL certificate needed? (optional)
10. ☐ Compliance considerations?

---

## Summary for Management

**What We Need:**

```
✅ 1 x Linux VM (Ubuntu 22.04)
✅ 4 vCPU, 8 GB RAM, 40 GB disk
✅ Network access from Zabbix server
✅ Estimated setup time: 2-3 hours
✅ Estimated monthly cost: $0 (if on-prem)
```

**What We Get:**

```
✅ AI-powered alert analysis
✅ Intelligent network monitoring
✅ 24/7 automated notifications
✅ Reduced incident response time
✅ Complete audit trail
```

---

**Document Version:** 1.0
**Last Updated:** 2026-04-21
**Status:** Ready for provisioning approval
