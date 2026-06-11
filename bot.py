import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, timedelta
from config import TELEGRAM_BOT_TOKEN, TIMEZONE
from database import init_db, get_session, User, Contest, Subscription
from contest_service import ContestService
from scheduler import ReminderScheduler

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class ContestBot:
    """Main Telegram bot class"""
    
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.contest_service = ContestService()
        self.reminder_scheduler = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command and callback handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("upcoming", self.upcoming))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe))
        self.application.add_handler(CommandHandler("reminder", self.set_reminder))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("weekly", self.weekly_digest))
        self.application.add_handler(CommandHandler("calendar", self.calendar_export))
        
        # Callback query handlers for buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        session = get_session()
        user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
        
        if not user:
            # Create new user
            user = User(
                telegram_id=update.effective_user.id,
                username=update.effective_user.username
            )
            session.add(user)
            session.commit()
        
        session.close()
        
        message = (
            "🚀 <b>Welcome to Contest Tracker!</b>\n\n"
            "Track upcoming programming contests from multiple platforms.\n\n"
            "<b>Available Commands:</b>\n"
            "/upcoming - Show upcoming contests\n"
            "/subscribe - Subscribe to platforms\n"
            "/unsubscribe - Unsubscribe from platforms\n"
            "/reminder - Set reminder preferences\n"
            "/weekly - Get weekly digest\n"
            "/calendar - Export to calendar\n"
            "/help - Show help message\n"
        )
        
        await update.message.reply_text(message, parse_mode="HTML")
    
    async def upcoming(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /upcoming command - Show next 10 contests"""
        session = get_session()
        
        # Fetch contests from API
        contests = self.contest_service.get_upcoming_contests(days_ahead=7, limit=10)
        self.contest_service.save_contests(contests)
        
        # Get from database filtered by user subscriptions
        user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
        
        if not user:
            user = User(telegram_id=update.effective_user.id)
            session.add(user)
            session.commit()
        
        db_contests = self.contest_service.get_contests_for_user(
            update.effective_user.id,
            days_ahead=7
        )
        
        if not db_contests:
            await update.message.reply_text("No upcoming contests found. Try subscribing to platforms first!")
            session.close()
            return
        
        message = "<b>📅 Upcoming Contests (Next 7 Days):</b>\n\n"
        
        for i, contest in enumerate(db_contests[:10], 1):
            start_time = contest.start_time.strftime("%Y-%m-%d %H:%M")
            message += (
                f"{i}. <b>{contest.name}</b>\n"
                f"   Platform: {contest.platform}\n"
                f"   Start: {start_time} UTC\n"
            )
            if contest.difficulty:
                message += f"   Difficulty: {contest.difficulty}\n"
            message += "\n"
        
        await update.message.reply_text(message, parse_mode="HTML")
        session.close()
    
    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /subscribe command"""
        if not context.args:
            message = (
                "Usage: /subscribe <platform>\n\n"
                "Available platforms: Codeforces, LeetCode, CodeChef, AtCoder, TopCoder, "
                "HackerEarth, HackerRank\n\n"
                "Example: /subscribe Codeforces"
            )
            await update.message.reply_text(message)
            return
        
        platform = " ".join(context.args).strip()
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
            
            # Check if already subscribed
            existing = session.query(Subscription).filter(
                Subscription.user_id == user.id,
                Subscription.platform == platform
            ).first()
            
            if existing:
                existing.subscribed = True
                session.commit()
                await update.message.reply_text(f"✅ Already subscribed to {platform}")
            else:
                subscription = Subscription(
                    user_id=user.id,
                    platform=platform,
                    subscribed=True
                )
                session.add(subscription)
                session.commit()
                await update.message.reply_text(f"✅ Subscribed to {platform}!")
        except Exception as e:
            logger.error(f"Error subscribing: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            session.close()
    
    async def unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /unsubscribe command"""
        if not context.args:
            await update.message.reply_text("Usage: /unsubscribe <platform>")
            return
        
        platform = " ".join(context.args).strip()
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
            
            subscription = session.query(Subscription).filter(
                Subscription.user_id == user.id,
                Subscription.platform == platform
            ).first()
            
            if subscription:
                subscription.subscribed = False
                session.commit()
                await update.message.reply_text(f"✅ Unsubscribed from {platform}")
            else:
                await update.message.reply_text(f"Not subscribed to {platform}")
        except Exception as e:
            logger.error(f"Error unsubscribing: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            session.close()
    
    async def set_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /reminder command"""
        message = (
            "⏰ <b>Reminder Settings</b>\n\n"
            "You can set reminders for upcoming contests.\n"
            "Default: 30 minutes before contest\n\n"
            "Use /upcoming to see contests and click the reminder button."
        )
        await update.message.reply_text(message, parse_mode="HTML")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_text = (
            "🤖 <b>Contest Tracker Bot - Help</b>\n\n"
            "<b>Commands:</b>\n"
            "/start - Start the bot\n"
            "/upcoming - Show upcoming contests\n"
            "/subscribe <platform> - Subscribe to a platform\n"
            "/unsubscribe <platform> - Unsubscribe from a platform\n"
            "/reminder - Manage reminder settings\n"
            "/weekly - Get weekly digest\n"
            "/calendar - Export contests to calendar\n"
            "/help - Show this message\n\n"
            "<b>Supported Platforms:</b>\n"
            "Codeforces, LeetCode, CodeChef, AtCoder, TopCoder, HackerEarth, HackerRank\n"
        )
        await update.message.reply_text(help_text, parse_mode="HTML")
    
    async def weekly_digest(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /weekly command - Send weekly digest"""
        session = get_session()
        user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
        
        # Get contests for this week
        contests = self.contest_service.get_contests_for_user(
            update.effective_user.id,
            days_ahead=7
        )
        
        if not contests:
            await update.message.reply_text("No contests this week!")
            session.close()
            return
        
        # Count by platform
        platform_count = {}
        for contest in contests:
            platform_count[contest.platform] = platform_count.get(contest.platform, 0) + 1
        
        message = f"📊 <b>Weekly Digest</b>\n\n<b>Total Contests: {len(contests)}</b>\n\n"
        
        for platform, count in platform_count.items():
            message += f"{platform}: {count}\n"
        
        await update.message.reply_text(message, parse_mode="HTML")
        session.close()
    
    async def calendar_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /calendar command - Export to ICS format"""
        await update.message.reply_text(
            "📅 Calendar export feature coming soon!\n\n"
            "This will generate an .ics file you can import to Google Calendar."
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button clicks"""
        query = update.callback_query
        await query.answer()
    
    def run(self):
        """Run the bot"""
        # Initialize database
        init_db()
        
        # Start reminder scheduler
        self.reminder_scheduler = ReminderScheduler(self.application.bot)
        self.reminder_scheduler.start()
        
        logger.info("Contest bot started!")
        self.application.run_polling()
    
    def stop(self):
        """Stop the bot"""
        if self.reminder_scheduler:
            self.reminder_scheduler.stop()
        logger.info("Contest bot stopped!")


if __name__ == "__main__":
    bot = ContestBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.stop()
