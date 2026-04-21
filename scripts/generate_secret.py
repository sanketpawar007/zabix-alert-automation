#!/usr/bin/env python3
"""
Generate a secure webhook secret
"""
import secrets

print("═" * 70)
print("🔐 Webhook Secret Generator")
print("═" * 70)
print("")
print("Your new webhook secret:")
print("")
print(secrets.token_hex(32))
print("")
print("Add this to your .env file as WEBHOOK_SECRET")
print("And use the SAME secret in your Zabbix webhook configuration!")
print("═" * 70)
