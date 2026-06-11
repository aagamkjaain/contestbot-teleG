# Contest Tracker Bot 🚀

A Telegram bot that tracks upcoming programming contests from multiple platforms using the CLIST API.

## Features

- 📅 **Track Contests**: Get upcoming contests from Codeforces, LeetCode, CodeChef, AtCoder, TopCoder, HackerEarth, HackerRank, and more
- 🔔 **Smart Reminders**: Automatic reminders 30 minutes before contest starts
- 🎯 **Platform Filters**: Subscribe/unsubscribe to specific platforms
- 📊 **Weekly Digest**: Get weekly statistics on upcoming contests
- 📱 **Calendar Export**: Export contests to Google Calendar (ICS format)
- ⭐ **Difficulty Ratings**: See estimated difficulty for each contest

## Tech Stack

- **Backend**: Python 3.8+
- **Bot Framework**: python-telegram-bot
- **API Client**: requests
- **Database**: SQLAlchemy + SQLite
- **Scheduler**: APScheduler
- **Environment**: python-dotenv

## Setup

### 1. Clone Repository
```bash
git clone <repo-url>
cd telebot
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create a `.env` file in the project root:

```env
# Get from BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_token_here

# Get from https://clist.by/api/v4/doc/
CLIST_USERNAME=your_username
CLIST_API_KEY=your_api_key

# Database configuration (optional)
DATABASE_URL=sqlite:///contests.db

# Timezone (optional)
TIMEZONE=UTC
```

### 5. Initialize Database
```bash
python -c "from database import init_db; init_db()"
```

### 6. Run the Bot
```bash
python bot.py
```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and register |
| `/upcoming` | Show next 10 upcoming contests |
| `/subscribe <platform>` | Subscribe to a platform |
| `/unsubscribe <platform>` | Unsubscribe from a platform |
| `/reminder` | Manage reminder settings |
| `/weekly` | Get weekly digest |
| `/calendar` | Export contests to calendar |
| `/help` | Show help message |

## Project Structure

```
contest_bot/
├── bot.py              # Main bot file with commands
├── config.py           # Configuration and environment variables
├── database.py         # SQLAlchemy models and database setup
├── contest_service.py  # CLIST API integration
├── scheduler.py        # Reminder scheduler
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not committed)
├── .env.example        # Example environment file
└── contests.db         # SQLite database (generated)
```

## Database Schema

### Users Table
Stores Telegram user information

### Contests Table
Stores fetched contests from CLIST API

### Reminders Table
Stores user reminder preferences for contests

### Subscriptions Table
Stores user's platform subscriptions

## Getting API Credentials

### Telegram Bot Token
1. Open Telegram and search for `@BotFather`
2. Use `/newbot` command
3. Copy the token provided

### CLIST API Credentials
1. Visit https://clist.by/api/v4/doc/
2. Sign up for an account
3. Generate API key from your profile
4. Use your username and API key for authentication

## Deployment

### Option 1: Railway
1. Push code to GitHub
2. Connect GitHub account to Railway
3. Create new project from repository
4. Add environment variables in Railway dashboard
5. Deploy!

### Option 2: Render
1. Push code to GitHub
2. Create new "Web Service" on Render
3. Connect GitHub repository
4. Add environment variables
5. Deploy!

### Option 3: Fly.io
1. Push code to GitHub
2. Install Fly CLI
3. Run `flyctl launch`
4. Add environment variables
5. Deploy with `flyctl deploy`

## Running Locally with Long Polling

The bot uses long polling by default, which works locally without any firewall configuration.

```bash
python bot.py
```

## Running with Webhooks (for production)

For production, consider using webhooks instead of polling:

1. Get a domain (free option: Render provides one)
2. Update bot.py to use webhooks instead of polling
3. Configure webhook URL in Telegram

## Troubleshooting

### Bot not responding
- Check TELEGRAM_BOT_TOKEN is correct
- Verify internet connection
- Check logs for errors

### Contests not fetching
- Verify CLIST credentials
- Check API key has proper permissions
- Ensure CLIST API is accessible

### Reminders not sending
- Check scheduler is running in logs
- Verify user is registered in database
- Check reminder preferences are set

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use for personal or commercial projects

## Support

For issues or questions, please open an issue in the repository.
