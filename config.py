import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# CLIST API Configuration
CLIST_USERNAME = os.getenv("CLIST_USERNAME")
CLIST_API_KEY = os.getenv("CLIST_API_KEY")
CLIST_BASE_URL = "https://clist.by/api/v4/contest/"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///contests.db")

# Timezone Configuration
TIMEZONE = os.getenv("TIMEZONE", "UTC")

# Reminder Settings
REMINDER_CHECK_INTERVAL = 60  # Check every 60 seconds

# Validate required configurations
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env file")
if not CLIST_USERNAME or not CLIST_API_KEY:
    raise ValueError("CLIST_USERNAME or CLIST_API_KEY is not set in .env file")
