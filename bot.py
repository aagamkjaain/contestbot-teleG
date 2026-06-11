import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
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


class DummyHTTPHandler(BaseHTTPRequestHandler):
    """Simple dummy handler for Render health checks"""
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")
        
    def log_message(self, format, *args):
        # Suppress request logging to keep output clean
        return


def start_dummy_server():
    """Start a dummy HTTP server in a daemon thread on $PORT"""
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHTTPHandler)
    logger.info(f"Starting dummy HTTP server on port {port} for Render health check...")
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server


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
        self.application.add_handler(CommandHandler("dsa", self.dsa_competitions))
        self.application.add_handler(CommandHandler("dsa_competitions", self.dsa_competitions))
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
            "/competitions - Show all contests (next 30 days & active)\n"
            "/dsa - Show DSA-only contests (Codeforces, LeetCode, etc.)\n"
            "/help - Show help message\n"
        )
        
        await update.message.reply_text(message, parse_mode="HTML")
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_text = (
            "🤖 <b>Contest Tracker Bot - Help</b>\n\n"
            "<b>Commands:</b>\n"
            "/start - Start the bot\n"
            "/competitions - Show all active and upcoming contests\n"
            "/dsa - Show DSA-only active and upcoming contests\n"
            "/help - Show this message\n\n"
            "Use the buttons on the message to navigate pages, toggle between active/upcoming contests, filter DSA-only, and force-refresh the data."
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

    async def dsa_competitions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle DSA-only competitions command"""
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
        
        # Send interactive browser starting on page 0 with "dsa" status
        await self.send_contests_browser(
            update_or_query=update,
            page=0,
            status="dsa",
            is_edit=False
        )

    async def send_contests_browser(self, update_or_query, page=0, status="upcoming", is_edit=False):
        """Send or edit the interactive competitions browser message"""
        if status == "active":
            contests = self.contest_service.get_active_contests(dsa_only=False)
        elif status == "dsa_active":
            contests = self.contest_service.get_active_contests(dsa_only=True)
        elif status == "dsa":
            contests = self.contest_service.get_filtered_contests(
                days_ahead=30,
                platform="All",
                difficulty="All",
                subscribed_only=False,
                dsa_only=True
            )
        else:
            # Get all upcoming contests for next 30 days
            contests = self.contest_service.get_filtered_contests(
                days_ahead=30,
                platform="All",
                difficulty="All",
                subscribed_only=False,
                dsa_only=False
            )
            
        PAGE_SIZE = 5
        total_contests = len(contests)
        total_pages = max(1, (total_contests + PAGE_SIZE - 1) // PAGE_SIZE)
        
        # Clamp page number
        page = max(0, min(page, total_pages - 1))
        
        start_idx = page * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        page_contests = contests[start_idx:end_idx]
        
        if status == "active":
            title = "🟢 <b>Active & Ongoing Competitions</b>"
        elif status == "dsa_active":
            title = "🟢💻 <b>Active DSA Competitions</b>"
        elif status == "dsa":
            title = "💻 <b>Upcoming DSA Competitions (30 Days)</b>"
        else:
            title = "📅 <b>Upcoming Competitions (Next 30 Days)</b>"
        
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
        
        # Row 2: Status Toggle (Show Active vs Show Upcoming & DSA vs All)
        toggle_row = []
        if status == "upcoming":
            toggle_row.append(InlineKeyboardButton("🟢 Show Active", callback_data="comp:0:active"))
            toggle_row.append(InlineKeyboardButton("💻 DSA Only", callback_data="comp:0:dsa"))
        elif status == "active":
            toggle_row.append(InlineKeyboardButton("📅 Show Upcoming", callback_data="comp:0:upcoming"))
            toggle_row.append(InlineKeyboardButton("💻 DSA Only", callback_data="comp:0:dsa_active"))
        elif status == "dsa":
            toggle_row.append(InlineKeyboardButton("🟢 Show Active DSA", callback_data="comp:0:dsa_active"))
            toggle_row.append(InlineKeyboardButton("🌐 Show All", callback_data="comp:0:upcoming"))
        elif status == "dsa_active":
            toggle_row.append(InlineKeyboardButton("📅 Show Upcoming DSA", callback_data="comp:0:dsa"))
            toggle_row.append(InlineKeyboardButton("🌐 Show All", callback_data="comp:0:active"))
            
        keyboard.append(toggle_row)
        
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
                    
                    if status in ("active", "dsa_active"):
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
        
        # Start dummy HTTP server for Render health checks
        self.http_server = None
        if os.environ.get("PORT") or os.environ.get("RENDER"):
            self.http_server = start_dummy_server()
        
        # Start reminder scheduler
        self.reminder_scheduler = ReminderScheduler(self.application.bot)
        self.reminder_scheduler.start()
        
        logger.info("Contest bot started!")
        self.application.run_polling()
    
    def stop(self):
        """Stop the bot"""
        if self.reminder_scheduler:
            self.reminder_scheduler.stop()
        if hasattr(self, "http_server") and self.http_server:
            self.http_server.shutdown()
            logger.info("Dummy HTTP server stopped!")
        logger.info("Contest bot stopped!")


if __name__ == "__main__":
    bot = ContestBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.stop()
