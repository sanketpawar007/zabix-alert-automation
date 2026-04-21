#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
# Test Alert Script
# Sends a test alert to the webhook endpoint
# ══════════════════════════════════════════════════════════════════════════════

set -e

# Configuration
SERVER_URL="${SERVER_URL:-http://localhost:5001}"
WEBHOOK_SECRET="${WEBHOOK_SECRET:-test-secret-123}"
ALERT_TYPE="${1:-interface_down}"

echo "════════════════════════════════════════════════════════════════════════════"
echo "🧪 Sending Test Alert"
echo "════════════════════════════════════════════════════════════════════════════"
echo "Server:      $SERVER_URL"
echo "Alert Type:  $ALERT_TYPE"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# Sample alert payloads based on type
case "$ALERT_TYPE" in
  "interface_down")
    ALERT_DATA='{
      "host": "juniper-core-router-01",
      "hostip": "192.168.1.1",
      "name": "Interface ge-0/0/1 is DOWN",
      "severity": "Disaster",
      "status": "PROBLEM",
      "value": "down(2)",
      "trigger": "Interface operational status changed to DOWN",
      "eventid": "12345",
      "time": "'$(date '+%Y-%m-%d %H:%M:%S')'"
    }'
    ;;

  "high_cpu")
    ALERT_DATA='{
      "host": "juniper-edge-router-02",
      "hostip": "192.168.1.2",
      "name": "High CPU utilization - 91%",
      "severity": "High",
      "status": "PROBLEM",
      "value": "91",
      "trigger": "CPU utilization above 85% for 5 minutes",
      "eventid": "12346",
      "time": "'$(date '+%Y-%m-%d %H:%M:%S')'"
    }'
    ;;

  "memory_high")
    ALERT_DATA='{
      "host": "juniper-distribution-switch-01",
      "hostip": "192.168.1.3",
      "name": "High memory utilization - 93%",
      "severity": "High",
      "status": "PROBLEM",
      "value": "93",
      "trigger": "Memory utilization above 90%",
      "eventid": "12347",
      "time": "'$(date '+%Y-%m-%d %H:%M:%S')'"
    }'
    ;;

  "resolved")
    ALERT_DATA='{
      "host": "juniper-core-router-01",
      "hostip": "192.168.1.1",
      "name": "Interface ge-0/0/1 is DOWN",
      "severity": "Disaster",
      "status": "RESOLVED",
      "value": "up(1)",
      "trigger": "Interface operational status changed to DOWN",
      "eventid": "12345",
      "time": "'$(date '+%Y-%m-%d %H:%M:%S')'"
    }'
    ;;

  *)
    echo "❌ Unknown alert type: $ALERT_TYPE"
    echo "Available types: interface_down, high_cpu, memory_high, resolved"
    exit 1
    ;;
esac

# Send the alert
echo "📤 Sending alert to webhook..."
echo ""

RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$SERVER_URL/webhook/zabbix" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: $WEBHOOK_SECRET" \
  -d "$ALERT_DATA")

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

echo "Response Code: $HTTP_CODE"
echo "Response Body: $BODY"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Test alert sent successfully!"
else
  echo "❌ Test alert failed with code: $HTTP_CODE"
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "Check your Telegram/WhatsApp for the notification!"
echo "════════════════════════════════════════════════════════════════════════════"
