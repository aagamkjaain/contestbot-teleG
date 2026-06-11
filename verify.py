#!/usr/bin/env python
"""
Pre-Deployment Verification Script
Checks all systems before deploying to Railway/Render/Fly.io

Run this script:
    python verify.py
"""

import sys
import os
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
CHECKMARK = '✅'
CROSS = '❌'
WARNING = '⚠️'

def print_header(text):
    """Print section header"""
    print(f"\n{BLUE}{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}{CHECKMARK} {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}{CROSS} {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}{WARNING} {text}{RESET}")

def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ️  {text}{RESET}")

def check_python_version():
    """Check Python version"""
    print_header("Python Version")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
        return False

def check_requirements():
    """Check if all required packages are installed"""
    print_header("Required Packages")
    
    required_packages = [
        ('telegram', 'python-telegram-bot'),
        ('requests', 'requests'),
        ('apscheduler', 'APScheduler'),
        ('dotenv', 'python-dotenv'),
        ('sqlalchemy', 'SQLAlchemy'),
    ]
    
    all_installed = True
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print_success(f"{package_name}")
        except ImportError:
            print_error(f"{package_name} NOT installed")
            all_installed = False
    
    if not all_installed:
        print_warning("Run: pip install -r requirements.txt")
    
    return all_installed

def check_env_file():
    """Check .env file exists and has required variables"""
    print_header(".env Configuration")
    
    if not os.path.exists('.env'):
        print_error(".env file not found")
        return False
    
    print_success(".env file found")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'CLIST_USERNAME',
        'CLIST_API_KEY',
    ]
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:10] + '...' if len(value) > 10 else value
            print_success(f"{var} = {masked_value}")
        else:
            print_error(f"{var} is missing or empty")
            all_present = False
    
    return all_present

def check_config():
    """Check configuration can be loaded"""
    print_header("Configuration Loading")
    
    try:
        from config import (
            TELEGRAM_BOT_TOKEN,
            CLIST_USERNAME,
            CLIST_API_KEY,
            CLIST_BASE_URL,
            DATABASE_URL,
            TIMEZONE
        )
        print_success("Config loaded successfully")
        print_info(f"Database: {DATABASE_URL}")
        print_info(f"Timezone: {TIMEZONE}")
        print_info(f"CLIST API: {CLIST_BASE_URL}")
        return True
    except Exception as e:
        print_error(f"Config loading failed: {str(e)}")
        return False

def check_database():
    """Check database initialization"""
    print_header("Database Setup")
    
    try:
        from database import init_db, Session, User, Contest, Reminder, Subscription
        
        # Initialize database
        init_db()
        print_success("Database initialized")
        
        # Check if we can create a session
        session = Session()
        print_success("Database connection works")
        
        # Get table counts
        user_count = session.query(User).count()
        contest_count = session.query(Contest).count()
        print_info(f"Users in DB: {user_count}")
        print_info(f"Contests in DB: {contest_count}")
        
        session.close()
        return True
    except Exception as e:
        print_error(f"Database check failed: {str(e)}")
        return False

def check_clist_api():
    """Check CLIST API connection"""
    print_header("CLIST API Connection")
    
    try:
        from contest_service import ContestService
        
        service = ContestService()
        print_info("Fetching test data from CLIST...")
        
        contests = service.get_upcoming_contests(days_ahead=7, limit=5)
        
        if contests:
            print_success(f"CLIST API working! Fetched {len(contests)} contests")
            print_info(f"Sample: {contests[0]['name']} on {contests[0]['platform']}")
            return True
        else:
            print_warning("CLIST API returned no contests (may be normal)")
            return True
    except Exception as e:
        print_error(f"CLIST API connection failed: {str(e)}")
        print_warning("Check CLIST_USERNAME and CLIST_API_KEY in .env")
        return False

def check_telegram_bot():
    """Check Telegram bot token validity"""
    print_header("Telegram Bot Token")
    
    try:
        from telegram import Bot
        from config import TELEGRAM_BOT_TOKEN
        
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        me = bot.get_me()
        
        print_success(f"Bot token is valid!")
        print_info(f"Bot name: @{me.username}")
        print_info(f"Bot ID: {me.id}")
        return True
    except Exception as e:
        print_error(f"Telegram bot token invalid: {str(e)}")
        print_warning("Get new token from @BotFather on Telegram")
        return False

def check_scheduler():
    """Check APScheduler can be initialized"""
    print_header("Scheduler (APScheduler)")
    
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        
        scheduler = BackgroundScheduler()
        print_success("APScheduler initialized successfully")
        
        # Check timezone
        from config import TIMEZONE
        print_info(f"Scheduler timezone: {TIMEZONE}")
        return True
    except Exception as e:
        print_error(f"APScheduler check failed: {str(e)}")
        return False

def check_bot_structure():
    """Check bot file structure"""
    print_header("Bot File Structure")
    
    required_files = [
        'bot.py',
        'config.py',
        'database.py',
        'contest_service.py',
        'scheduler.py',
        'utils.py',
        'main.py',
        'requirements.txt',
        '.env',
        '.gitignore',
        'README.md',
    ]
    
    all_present = True
    for filename in required_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print_success(f"{filename} ({size} bytes)")
        else:
            print_error(f"{filename} NOT FOUND")
            all_present = False
    
    return all_present

def run_all_checks():
    """Run all verification checks"""
    print(f"\n{BLUE}{'='*50}")
    print(f"  Contest Tracker Bot - Pre-Deployment Check")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}{RESET}\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("File Structure", check_bot_structure),
        ("Required Packages", check_requirements),
        (".env Configuration", check_env_file),
        ("Configuration Loading", check_config),
        ("Database Setup", check_database),
        ("Telegram Bot", check_telegram_bot),
        ("CLIST API", check_clist_api),
        ("Scheduler", check_scheduler),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_error(f"Unexpected error in {check_name}: {str(e)}")
            results.append((check_name, False))
    
    # Print summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = f"{GREEN}{CHECKMARK} PASS{RESET}" if result else f"{RED}{CROSS} FAIL{RESET}"
        print(f"  {status} - {check_name}")
    
    print(f"\n{BLUE}Result: {passed}/{total} checks passed{RESET}\n")
    
    if passed == total:
        print_success("All systems ready for deployment! ✨")
        print_info("Next steps:")
        print_info("1. Go to railway.app")
        print_info("2. Connect your GitHub repository")
        print_info("3. Add environment variables")
        print_info("4. Click Deploy!")
        return True
    else:
        print_error("Some checks failed - fix issues above before deploying")
        print_warning("See DEPLOYMENT.md for troubleshooting")
        return False

if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
