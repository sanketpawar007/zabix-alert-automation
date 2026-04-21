#!/usr/bin/env python3
"""
Telegram Bot Setup Helper
Helps you get your Telegram chat ID
"""
import sys
import requests


def get_chat_id(bot_token):
    """Get chat ID from Telegram bot"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if not data.get('ok'):
            print("❌ Error: Invalid bot token or API error")
            return None

        updates = data.get('result', [])

        if not updates:
            print("⚠️  No messages found!")
            print("")
            print("📱 Please do the following:")
            print("   1. Open Telegram")
            print("   2. Search for your bot")
            print("   3. Send any message to your bot (e.g., '/start' or 'hello')")
            print("   4. Run this script again")
            return None

        print("✅ Found messages! Here are your chat IDs:")
        print("")

        chat_ids = set()
        for update in updates:
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                chat_type = update['message']['chat']['type']
                username = update['message']['chat'].get('username', 'N/A')
                first_name = update['message']['chat'].get('first_name', '')
                last_name = update['message']['chat'].get('last_name', '')
                full_name = f"{first_name} {last_name}".strip()

                chat_ids.add(chat_id)

                print(f"📍 Chat ID: {chat_id}")
                print(f"   Type: {chat_type}")
                print(f"   Name: {full_name}")
                if username != 'N/A':
                    print(f"   Username: @{username}")
                print("")

        if chat_ids:
            print("═" * 70)
            print("✨ Add this to your .env file:")
            print("═" * 70)
            print(f"TELEGRAM_CHAT_IDS={','.join(map(str, chat_ids))}")
            print("═" * 70)

        return chat_ids

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    print("═" * 70)
    print("🤖 Telegram Bot Setup Helper")
    print("═" * 70)
    print("")

    if len(sys.argv) > 1:
        bot_token = sys.argv[1]
    else:
        print("Enter your Telegram bot token:")
        print("(Get it from @BotFather on Telegram)")
        print("")
        bot_token = input("Bot Token: ").strip()

    if not bot_token:
        print("❌ Bot token is required!")
        sys.exit(1)

    print("")
    print("🔍 Fetching chat IDs...")
    print("")

    get_chat_id(bot_token)


if __name__ == '__main__':
    main()
