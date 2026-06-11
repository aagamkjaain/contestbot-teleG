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

PLATFORMS = ["Codeforces", "LeetCode", "CodeChef", "AtCoder", "TopCoder", "HackerEarth", "HackerRank"]
DIFFICULTIES = ["All", "Easy", "Intermediate", "Hard"]


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
        self.application.add_handler(CommandHandler("upcoming30", self.upcoming30))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe))
        self.application.add_handler(CommandHandler("subscribeall", self.subscribe_all))
        self.application.add_handler(CommandHandler("subscribe_all", self.subscribe_all))
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
            "/upcoming - Show upcoming contests (7 days)\n"
            "/upcoming30 - Show upcoming contests (30 days)\n"
            "/subscribe - Subscribe to platforms\n"
            "/subscribeall - Subscribe to all platforms at once\n"
            "/unsubscribe - Unsubscribe from platforms\n"
            "/reminder - Set reminder preferences\n"
            "/weekly - Get weekly digest\n"
            "/calendar - Export to calendar\n"
            "/help - Show help message\n"
        )
        
        await update.message.reply_text(message, parse_mode="HTML")
    
    async def upcoming(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /upcoming command - Show next 7 days contests in an interactive browser"""
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
            
        # Get count of subscriptions to set smart default for sub_only_val
        sub_count = session.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.subscribed == True
        ).count()
        session.close()
        
        sub_only_val = 1 if sub_count > 0 else 0
        
        # Fetch latest contests (caches for 5 mins unless forced)
        contests = self.contest_service.get_upcoming_contests(days_ahead=7)
        self.contest_service.save_contests(contests)
        
        await self.send_contests_browser(
            update_or_query=update,
            user_id=user_id,
            days_ahead=7,
            page=0,
            platform_idx=0,
            diff_idx=0,
            sub_only_val=sub_only_val,
            is_edit=False
        )

    async def upcoming30(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /upcoming30 command - Show next 30 days contests in an interactive browser"""
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
            
        # Get count of subscriptions to set smart default for sub_only_val
        sub_count = session.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.subscribed == True
        ).count()
        session.close()
        
        sub_only_val = 1 if sub_count > 0 else 0
        
        # Fetch latest contests (caches for 5 mins unless forced)
        contests = self.contest_service.get_upcoming_contests(days_ahead=30)
        self.contest_service.save_contests(contests)
        
        await self.send_contests_browser(
            update_or_query=update,
            user_id=user_id,
            days_ahead=30,
            page=0,
            platform_idx=0,
            diff_idx=0,
            sub_only_val=sub_only_val,
            is_edit=False
        )

    async def subscribe_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /subscribeall command"""
        session = get_session()
        try:
            # Ensure user exists
            user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
            if not user:
                user = User(
                    telegram_id=update.effective_user.id,
                    username=update.effective_user.username
                )
                session.add(user)
                session.commit()
            
            # Subscribe to all platforms
            for platform in PLATFORMS:
                existing = session.query(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.platform == platform
                ).first()
                if existing:
                    existing.subscribed = True
                else:
                    subscription = Subscription(
                        user_id=user.id,
                        platform=platform,
                        subscribed=True
                    )
                    session.add(subscription)
            
            session.commit()
            
            message = (
                "✅ <b>Successfully subscribed to all platforms!</b>\n\n"
                f"You will now track: {', '.join(PLATFORMS)}."
            )
            await update.message.reply_text(message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error subscribing to all: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            session.close()

    async def send_contests_browser(self, update_or_query, user_id, days_ahead=30, page=0, platform_idx=0, diff_idx=0, sub_only_val=0, is_edit=False):
        """Send or edit the interactive contest browser message"""
        platform_filter = "All" if platform_idx == 0 else PLATFORMS[platform_idx - 1]
        difficulty_filter = DIFFICULTIES[diff_idx]
        sub_only = bool(sub_only_val)
        
        contests = self.contest_service.get_filtered_contests(
            user_id=user_id,
            days_ahead=days_ahead,
            platform=platform_filter,
            difficulty=difficulty_filter,
            subscribed_only=sub_only
        )
        
        PAGE_SIZE = 5
        total_contests = len(contests)
        total_pages = max(1, (total_contests + PAGE_SIZE - 1) // PAGE_SIZE)
        
        # Clamp page number
        page = max(0, min(page, total_pages - 1))
        
        start_idx = page * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        page_contests = contests[start_idx:end_idx]
        
        message = (
            f"📅 <b>Upcoming Contests (Next {days_ahead} Days)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Filter: <b>{'Only Subscribed' if sub_only else 'All Platforms'}</b>\n"
            f"🏷️ Platform: <b>{platform_filter}</b>\n"
            f"⚡ Difficulty: <b>{difficulty_filter}</b>\n"
            f"📄 Page: <b>{page + 1} of {total_pages}</b> (Total: {total_contests})\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        if not page_contests:
            message += "❌ <i>No contests found matching the current filters.</i>\n"
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
            nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"br:{page-1}:{days_ahead}:{platform_idx}:{diff_idx}:{sub_only_val}"))
        else:
            nav_row.append(InlineKeyboardButton("▪️", callback_data="none"))
            
        nav_row.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="none"))
        
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"br:{page+1}:{days_ahead}:{platform_idx}:{diff_idx}:{sub_only_val}"))
        else:
            nav_row.append(InlineKeyboardButton("▪️", callback_data="none"))
            
        keyboard.append(nav_row)
        
        # Row 2: Filter selectors
        filter_row = [
            InlineKeyboardButton("🏷️ Platform", callback_data=f"br_fplat:{page}:{days_ahead}:{platform_idx}:{diff_idx}:{sub_only_val}"),
            InlineKeyboardButton("⚡ Difficulty", callback_data=f"br_fdiff:{page}:{days_ahead}:{platform_idx}:{diff_idx}:{sub_only_val}")
        ]
        keyboard.append(filter_row)
        
        # Row 3: Subscription toggle & Refresh
        sub_label = "🔔 Subscribed Only" if sub_only else "🔕 All Platforms"
        next_sub_only = 0 if sub_only else 1
        util_row = [
            InlineKeyboardButton(sub_label, callback_data=f"br:{page}:{days_ahead}:{platform_idx}:{diff_idx}:{next_sub_only}"),
            InlineKeyboardButton("🔄 Refresh", callback_data=f"br_ref:{page}:{days_ahead}:{platform_idx}:{diff_idx}:{sub_only_val}")
        ]
        keyboard.append(util_row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_edit:
            await update_or_query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview=True)
        else:
            await update_or_query.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview=True)

    async def send_platform_filter_menu(self, query, days, page, platform_idx, diff_idx, sub_only_val):
        """Show platform selection menu"""
        keyboard = []
        
        # All Platforms button
        keyboard.append([InlineKeyboardButton("✨ All Platforms", callback_data=f"br:0:{days}:0:{diff_idx}:{sub_only_val}")])
        
        # Specific platforms grid
        row = []
        for i, plat in enumerate(PLATFORMS, 1):
            # Show a checkmark next to the active platform
            active_marker = " ✅" if i == platform_idx else ""
            row.append(InlineKeyboardButton(f"{plat}{active_marker}", callback_data=f"br:0:{days}:{i}:{diff_idx}:{sub_only_val}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
            
        # Back button
        keyboard.append([InlineKeyboardButton("🔙 Back to Contests", callback_data=f"br:{page}:{days}:{platform_idx}:{diff_idx}:{sub_only_val}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔍 <b>Select Platform Filter:</b>",
            parse_mode="HTML",
            reply_markup=reply_markup
        )

    async def send_difficulty_filter_menu(self, query, days, page, platform_idx, diff_idx, sub_only_val):
        """Show difficulty selection menu"""
        keyboard = []
        
        # Difficulty options grid
        row = []
        for i, diff in enumerate(DIFFICULTIES):
            # Show a checkmark next to the active difficulty
            active_marker = " ✅" if i == diff_idx else ""
            row.append(InlineKeyboardButton(f"{diff}{active_marker}", callback_data=f"br:0:{days}:{platform_idx}:{i}:{sub_only_val}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
            
        # Back button
        keyboard.append([InlineKeyboardButton("🔙 Back to Contests", callback_data=f"br:{page}:{days}:{platform_idx}:{diff_idx}:{sub_only_val}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔍 <b>Select Difficulty Filter:</b>",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    
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
            if not user:
                user = User(
                    telegram_id=update.effective_user.id,
                    username=update.effective_user.username
                )
                session.add(user)
                session.commit()
            
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
            if not user:
                user = User(
                    telegram_id=update.effective_user.id,
                    username=update.effective_user.username
                )
                session.add(user)
                session.commit()
            
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
            "/upcoming - Show upcoming contests (7 days)\n"
            "/upcoming30 - Show upcoming contests (30 days)\n"
            "/subscribe <platform> - Subscribe to a platform\n"
            "/subscribeall - Subscribe to all platforms at once\n"
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
        data = query.data
        
        if data == "none":
            await query.answer()
            return
            
        await query.answer()
        
        # Parse callback data
        try:
            parts = data.split(":")
            action = parts[0]
            
            # Action: br (browse list)
            if action in ("br", "br_ref"):
                page = int(parts[1])
                days = int(parts[2])
                platform_idx = int(parts[3])
                diff_idx = int(parts[4])
                sub_only_val = int(parts[5])
                
                # If refreshing, fetch new data from API first
                if action == "br_ref":
                    await query.edit_message_text("🔄 <i>Updating contests from CLIST... Please wait...</i>", parse_mode="HTML")
                    contests = self.contest_service.get_upcoming_contests(days_ahead=days, force=True)
                    self.contest_service.save_contests(contests)
                
                await self.send_contests_browser(
                    update_or_query=query,
                    user_id=query.from_user.id,
                    days_ahead=days,
                    page=page,
                    platform_idx=platform_idx,
                    diff_idx=diff_idx,
                    sub_only_val=sub_only_val,
                    is_edit=True
                )
            
            # Action: br_fplat (filter platform)
            elif action == "br_fplat":
                page = int(parts[1])
                days = int(parts[2])
                platform_idx = int(parts[3])
                diff_idx = int(parts[4])
                sub_only_val = int(parts[5])
                
                await self.send_platform_filter_menu(
                    query=query,
                    days=days,
                    page=page,
                    platform_idx=platform_idx,
                    diff_idx=diff_idx,
                    sub_only_val=sub_only_val
                )
                
            # Action: br_fdiff (filter difficulty)
            elif action == "br_fdiff":
                page = int(parts[1])
                days = int(parts[2])
                platform_idx = int(parts[3])
                diff_idx = int(parts[4])
                sub_only_val = int(parts[5])
                
                await self.send_difficulty_filter_menu(
                    query=query,
                    days=days,
                    page=page,
                    platform_idx=platform_idx,
                    diff_idx=diff_idx,
                    sub_only_val=sub_only_val
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
