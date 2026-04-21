# 🔧 Juniper Device Configuration Requirements

## Overview

**Do We Need Access?**

- ✅ **YES** - Need to verify SNMP is enabled and configured
- ⚠️ **BUT** - Likely already configured for existing Zabbix monitoring
- ℹ️ If Zabbix is already monitoring these devices, SNMP is already working!

---

## Quick Check: Is SNMP Already Working?

### Test from Zabbix Server

```bash
# SSH to your Zabbix server
ssh zabbix-server

# Test SNMP to a Juniper device
snmpwalk -v 2c -c YOUR_COMMUNITY_STRING JUNIPER_IP sysDescr

# If you see output like this, SNMP is already working:
# SNMPv2-MIB::sysDescr.0 = STRING: Juniper Networks, Inc. ex4300-48t
```

**If this works:** ✅ No changes needed on Juniper devices!

**If this fails:** ⚠️ Need to configure SNMP (see below)

---

## What Zabbix Already Monitors

If Zabbix is currently monitoring your Juniper devices, it's already collecting:

✅ Device reachability (ICMP ping)
✅ Interface status (up/down)
✅ Interface traffic (in/out)
✅ CPU utilization
✅ Memory usage
✅ Hardware status
✅ Temperature sensors

**Our AI alert system uses the SAME data** → No additional configuration needed on Juniper!

---

## If SNMP Is NOT Configured

### Requirements for Juniper Team

**What needs to be configured:**
1. Enable SNMP v2c (read-only)
2. Set community string
3. Restrict access to Zabbix server IP only

### Configuration Commands

Provide these to your Juniper/Network team:

```junos
# SSH to Juniper device
ssh admin@juniper-device

# Enter configuration mode
configure

# Set location and contact (optional but recommended)
set snmp location "DataCenter-Building-A-Rack-12"
set snmp contact "network-ops@yourcompany.com"

# Create SNMP v2c community (read-only)
# Replace 'YourSecureString' with a strong password
set snmp community YourSecureString authorization read-only

# IMPORTANT: Restrict access to Zabbix server IP ONLY
# Replace 192.168.1.100 with your Zabbix server IP
set snmp community YourSecureString clients 192.168.1.100/32

# Commit configuration
commit and-quit
```

---

## Verification Steps

### From Zabbix Server

```bash
# Test SNMP connectivity
snmpwalk -v 2c -c YourCommunityString JUNIPER_IP system

# Test specific OIDs
# System description
snmpget -v 2c -c YourCommunityString JUNIPER_IP sysDescr.0

# Uptime
snmpget -v 2c -c YourCommunityString JUNIPER_IP sysUpTime.0

# Interface count
snmpget -v 2c -c YourCommunityString JUNIPER_IP ifNumber.0
```

### From Juniper Device

```junos
# Show SNMP configuration
show snmp

# Show SNMP statistics
show snmp statistics

# Show SNMP communities
show snmp community

# Show active SNMP clients
show snmp mib walk system
```

---

## What Data Will Be Monitored

### Standard SNMP Data (Already in Zabbix)

| Metric | OID | What It Shows |
|--------|-----|---------------|
| **System Info** | sysDescr | Device model and JunOS version |
| **Uptime** | sysUpTime | Time since last reboot |
| **CPU** | jnxOperatingCPU | CPU utilization percentage |
| **Memory** | jnxOperatingBuffer | Memory usage percentage |
| **Interface Status** | ifOperStatus | Interface up/down state |
| **Interface Traffic** | ifHCInOctets, ifHCOutOctets | Traffic in/out (bytes) |
| **Interface Errors** | ifInErrors, ifOutErrors | Error counters |
| **Temperature** | jnxOperatingTemp | Device temperature |

### Juniper-Specific MIBs (Advanced)

These are available if you want more detailed monitoring:

```
JUNIPER-MIB → General Juniper information
JUNIPER-CHASSIS-MIB → Hardware components status
JUNIPER-IF-MIB → Interface statistics
JUNIPER-PING-MIB → RPM probe results
JUNIPER-ALARM-MIB → System alarms
```

---

## Security Considerations

### ✅ Secure SNMP Configuration

```junos
# Use strong community strings (like passwords)
set snmp community "zBx9mK2pLq8nR4sT" authorization read-only

# Restrict to Zabbix IP ONLY
set snmp community "zBx9mK2pLq8nR4sT" clients 192.168.1.100/32

# Enable only on management interface (if applicable)
set snmp interface ge-0/0/0.0

# Set trap targets (optional - for instant alerts)
set snmp trap-group ZABBIX version v2
set snmp trap-group ZABBIX targets 192.168.1.100
```

### ❌ Insecure Practices (DO NOT DO)

```
❌ Do NOT use default community strings (public, private)
❌ Do NOT allow SNMP from 0.0.0.0/0 (entire internet)
❌ Do NOT use SNMP write access (authorization read-write)
❌ Do NOT forget to commit configuration changes
```

---

## SNMP Versions Comparison

| Feature | SNMPv1 | SNMPv2c | SNMPv3 |
|---------|--------|---------|---------|
| **Authentication** | Community string | Community string | Username + Password |
| **Encryption** | ❌ No | ❌ No | ✅ Yes (AES/DES) |
| **Security** | Low | Low | High |
| **Compatibility** | ✅ Universal | ✅ Universal | ⚠️ Needs configuration |
| **Performance** | Good | Better (bulk requests) | Good |
| **Complexity** | Simple | Simple | Complex |

**Recommendation:** Use **SNMPv2c** for simplicity + performance.
**For high security:** Use **SNMPv3** (requires additional setup).

---

## Common Juniper Device Models

### Supported Models (All Juniper with JunOS)

✅ **EX Series** (Switches)
- EX2300, EX3400, EX4300, EX4600, EX9200, etc.

✅ **QFX Series** (Data Center Switches)
- QFX5100, QFX5200, QFX10000, etc.

✅ **MX Series** (Routers)
- MX80, MX204, MX480, MX960, etc.

✅ **SRX Series** (Firewalls)
- SRX300, SRX345, SRX1500, SRX4600, etc.

✅ **PTX Series** (Packet Transport)
- PTX1000, PTX3000, PTX10000, etc.

**Note:** All models support SNMP monitoring. Configuration is the same.

---

## Firewall Requirements (On Juniper Device)

If your Juniper devices have security zones/firewall rules:

```junos
# Allow SNMP from Zabbix server
set security zones security-zone trust interfaces ge-0/0/0.0
set security policies from-zone untrust to-zone trust policy allow-snmp match source-address ZABBIX-SERVER
set security policies from-zone untrust to-zone trust policy allow-snmp match destination-address any
set security policies from-zone untrust to-zone trust policy allow-snmp match application junos-snmp
set security policies from-zone untrust to-zone trust policy allow-snmp then permit

# Commit
commit
```

**Ports to Allow:**
- UDP 161 (SNMP queries - Zabbix → Juniper)
- UDP 162 (SNMP traps - Juniper → Zabbix) [optional]

---

## Checklist for Network Team

### Pre-Implementation

```
☐ Identify all Juniper devices to monitor
☐ Document current Zabbix monitoring status
☐ Get list of device IPs and hostnames
☐ Verify Zabbix can reach devices (ping test)

☐ For each device:
  ☐ SNMP already enabled? (check with Zabbix team)
  ☐ If yes: Document community string
  ☐ If no: Follow configuration steps above
  ☐ Verify SNMP v2c is working
  ☐ Confirm Zabbix server IP is whitelisted
```

### Configuration

```
☐ Generate strong community string
☐ Apply SNMP configuration to all devices
☐ Restrict access to Zabbix IP only
☐ Test SNMP queries from Zabbix server
☐ Document configuration in change management
```

### Verification

```
☐ Run snmpwalk test from Zabbix server
☐ Check Zabbix is receiving data
☐ Verify CPU, memory, interface metrics visible
☐ Test interface up/down detection
☐ Document community strings securely
```

---

## Integration with Zabbix

### Zabbix Configuration (For Reference)

If setting up new monitoring, Zabbix needs:

1. **Host Configuration:**
   - Add Juniper device as host
   - Set IP address
   - Set SNMP interface

2. **Template:**
   - Apply "Template Net Juniper SNMPv2" template
   - Or use "Template Net Network Generic Device SNMPv2"

3. **SNMP Settings:**
   - SNMP version: SNMPv2
   - Community: {$SNMP_COMMUNITY}
   - Port: 161

4. **Macros:**
   ```
   {$SNMP_COMMUNITY} = YourCommunityString
   {$ICMP_LOSS_WARN} = 20
   {$ICMP_RESPONSE_TIME_WARN} = 0.15
   ```

---

## Troubleshooting

### SNMP Not Working

**Problem:** `snmpwalk` returns timeout

**Possible Causes:**
1. ❌ SNMP not enabled on device
2. ❌ Wrong community string
3. ❌ Firewall blocking UDP 161
4. ❌ Zabbix IP not in clients list
5. ❌ SNMP daemon not running on device

**Solution:**
```junos
# On Juniper device
show snmp
show configuration snmp

# Check if SNMP process is running
show system processes | match snmp

# Check firewall
show security policies | match snmp
```

### Wrong Data Returned

**Problem:** SNMP works but returns incorrect data

**Solution:**
```bash
# Test specific OIDs
snmpget -v 2c -c COMMUNITY DEVICE_IP OID

# Example: Test CPU
snmpget -v 2c -c COMMUNITY DEVICE_IP .1.3.6.1.4.1.2636.3.1.13.1.8.1

# Load correct MIBs
export MIBS=+ALL
snmpwalk -v 2c -c COMMUNITY DEVICE_IP jnxOperatingCPU
```

---

## Documents to Share with Network Team

**For Juniper/Network Team:**

1. **This document** (`JUNIPER_DEVICE_SETUP.md`)
2. Configuration commands (copy-paste ready)
3. Verification commands
4. Security best practices

**Information Needed FROM Network Team:**

```
☐ List of Juniper device IPs
☐ Current SNMP status (enabled/disabled)
☐ If enabled: Community string
☐ Zabbix server IP address
☐ Access to test from Zabbix server
```

---

## Timeline

| Task | Duration | Owner | Status |
|------|----------|-------|--------|
| **Check current SNMP status** | 30 min | Network Team | ⏳ Pending |
| **If needed: Configure SNMP** | 1-2 hours | Network Team | ⏳ Pending |
| **Test from Zabbix** | 30 min | You + Network | ⏳ Pending |
| **Verify Zabbix data** | 30 min | You + Zabbix Admin | ⏳ Pending |

**Total Time:** 2-4 hours (if SNMP needs configuration)
**If SNMP already working:** 0 hours (no changes needed!)

---

## Summary for Your Senior

**Juniper Device Requirements:**

```
✅ IF already monitored by Zabbix:
   → No changes needed on Juniper devices
   → Verify SNMP is working (30 min test)

❌ IF not monitored by Zabbix:
   → Configure SNMP on each device (2-4 hours)
   → Network team needs to apply config
   → Test and verify

🔐 Security:
   → Read-only SNMP access
   → Restricted to Zabbix IP only
   → Strong community strings
```

**Questions to Ask:**
1. Are our Juniper devices already monitored in Zabbix?
2. If yes, can we get the SNMP community string?
3. If no, can network team configure SNMP?

---

**Document Version:** 1.0
**Last Updated:** 2026-04-21
**Status:** Ready for network team review
