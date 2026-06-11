import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, timedelta
from config import TELEGRAM_BOT_TOKEN
from database import init_db, get_session, User, Contest
from contest_service import ContestService
from scheduler import ReminderScheduler

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class ContestBot:
    """Main Telegram bot class with simplified competitions browsing"""
    
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.contest_service = ContestService()
        self.reminder_scheduler = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command and callback handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("competitions", self.competitions))
        self.application.add_handler(CommandHandler("show_competitions", self.competitions))
        self.application.add_handler(CommandHandler("upcoming", self.competitions))
        self.application.add_handler(CommandHandler("upcoming30", self.competitions))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
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
            "Track active/ongoing and upcoming programming contests.\n\n"
            "<b>Available Commands:</b>\n"
            "/competitions - Show contests browser (next 30 days & active)\n"
            "/help - Show help message\n"
        )
        
        await update.message.reply_text(message, parse_mode="HTML")
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_text = (
            "🤖 <b>Contest Tracker Bot - Help</b>\n\n"
            "<b>Commands:</b>\n"
            "/start - Start the bot\n"
            "/competitions - Show active and upcoming contests (aliases: /show_competitions, /upcoming)\n"
            "/help - Show this message\n\n"
            "Use the buttons on the message to navigate pages, toggle between active/upcoming contests, and force-refresh the data."
        )
        await update.message.reply_text(help_text, parse_mode="HTML")

    async def competitions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle competitions command (upcoming 30 days)"""
        user_id = update.effective_user.id
        
        # Ensure user exists in database
        session = get_session()
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            user = User(
                telegram_id=user_id,
                username=update.effective_user.username
            )
            session.add(user)
            session.commit()
        session.close()
        
        # Fetch upcoming contests first to ensure DB is populated
        contests = self.contest_service.get_upcoming_contests(days_ahead=30, force=False, active=False)
        self.contest_service.save_contests(contests)
        
        # Also fetch active contests to ensure DB has active ones populated
        active_contests = self.contest_service.get_upcoming_contests(force=False, active=True)
        self.contest_service.save_contests(active_contests)
        
        # Send interactive browser starting on page 0 with "upcoming" status
        await self.send_contests_browser(
            update_or_query=update,
            page=0,
            status="upcoming",
            is_edit=False
        )

    async def send_contests_browser(self, update_or_query, page=0, status="upcoming", is_edit=False):
        """Send or edit the interactive competitions browser message"""
        if status == "active":
            contests = self.contest_service.get_active_contests()
        else:
            # Get all upcoming contests for next 30 days
            contests = self.contest_service.get_filtered_contests(
                days_ahead=30,
                platform="All",
                difficulty="All",
                subscribed_only=False
            )
            
        PAGE_SIZE = 5
        total_contests = len(contests)
        total_pages = max(1, (total_contests + PAGE_SIZE - 1) // PAGE_SIZE)
        
        # Clamp page number
        page = max(0, min(page, total_pages - 1))
        
        start_idx = page * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        page_contests = contests[start_idx:end_idx]
        
        title = "🟢 <b>Active & Ongoing Competitions</b>" if status == "active" else "📅 <b>Upcoming Competitions (Next 30 Days)</b>"
        
        message = (
            f"{title}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📄 Page: <b>{page + 1} of {total_pages}</b> (Total: {total_contests})\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        if not page_contests:
            message += f"❌ <i>No {status} competitions found. Try refreshing!</i>\n"
        else:
            for idx, contest in enumerate(page_contests, start_idx + 1):
                start_time = contest.start_time.strftime("%Y-%m-%d %H:%M")
                
                # Calculate duration in human readable format
                duration_str = ""
                if contest.duration:
                    hours = contest.duration // 3600
                    minutes = (contest.duration % 3600) // 60
                    duration_str = f" ({hours}h {minutes}m)"
                
                message += (
                    f"{idx}. <b>{contest.name}</b>\n"
                    f"   Platform: {contest.platform}\n"
                    f"   Starts: <code>{start_time} UTC</code>{duration_str}\n"
                )
                if contest.difficulty:
                    message += f"   Difficulty: {contest.difficulty}\n"
                message += f"   🔗 <a href='{contest.url}'>Join Contest</a>\n\n"
                
        # Build Keyboard
        keyboard = []
        
        # Row 1: Pagination
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"comp:{page-1}:{status}"))
        else:
            nav_row.append(InlineKeyboardButton("▪️", callback_data="none"))
            
        nav_row.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="none"))
        
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"comp:{page+1}:{status}"))
        else:
            nav_row.append(InlineKeyboardButton("▪️", callback_data="none"))
            
        keyboard.append(nav_row)
        
        # Row 2: Status Toggle (Show Active vs Show Upcoming)
        if status == "upcoming":
            toggle_btn = InlineKeyboardButton("🟢 Show Active Competitions", callback_data="comp:0:active")
        else:
            toggle_btn = InlineKeyboardButton("📅 Show Upcoming (30 Days)", callback_data="comp:0:upcoming")
        keyboard.append([toggle_btn])
        
        # Row 3: Refresh
        keyboard.append([InlineKeyboardButton("🔄 Refresh List", callback_data=f"comp_ref:{page}:{status}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_edit:
            await update_or_query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview=True)
        else:
            await update_or_query.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview=True)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button clicks"""
        query = update.callback_query
        data = query.data
        
        if data == "none":
            await query.answer()
            return
            
        await query.answer()
        
        try:
            parts = data.split(":")
            action = parts[0]
            
            if action in ("comp", "comp_ref"):
                page = int(parts[1])
                status = parts[2]
                
                # If refreshing, fetch new data from API first
                if action == "comp_ref":
                    await query.edit_message_text("🔄 <i>Updating competitions from CLIST... Please wait...</i>", parse_mode="HTML")
                    
                    if status == "active":
                        # Fetch active contests
                        contests = self.contest_service.get_upcoming_contests(force=True, active=True)
                    else:
                        # Fetch upcoming contests
                        contests = self.contest_service.get_upcoming_contests(days_ahead=30, force=True, active=False)
                        
                    self.contest_service.save_contests(contests)
                
                await self.send_contests_browser(
                    update_or_query=query,
                    page=page,
                    status=status,
                    is_edit=True
                )
        except Exception as e:
            logger.error(f"Error handling button callback: {e}", exc_info=True)
    
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
