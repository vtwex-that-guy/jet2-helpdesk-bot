# ✈️ Jet2 Helpdesk Discord Bot

A lightweight modmail bot for Jet2 staff support via Discord.

## Features

- `/modmail`: Open a helpdesk ticket
- `/reply`: Respond to users
- `/close`: Close a ticket
- SQLite for tracking ticket status

## Setup

```bash
pip install -r requirements.txt
python bot.py
```

Create a `config.json` in the root:

```json
{
  "token": "YOUR_DISCORD_BOT_TOKEN",
  "guild_id": "YOUR_GUILD_ID",
  "modmail_channel_id": "MODMAIL_CHANNEL_ID",
  "admin_roles": ["Helpdesk", "Admin"]
}
```
