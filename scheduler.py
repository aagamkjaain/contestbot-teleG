from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from database import Session, User, Contest, Reminder, get_session
from config import TIMEZONE
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Handles scheduling and sending reminders for contests"""
    
    def __init__(self, bot):
        """
        Initialize the scheduler
        
        Args:
            bot: Telegram bot instance
        """
        self.bot = bot
        self.scheduler = BackgroundScheduler(timezone=TIMEZONE)
        self.session = get_session()
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.add_job(
            self.check_and_send_reminders,
            IntervalTrigger(seconds=60),  # Check every 60 seconds
            id="reminder_checker",
            name="Check and send contest reminders"
        )
        self.scheduler.start()
        logger.info("Reminder scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Reminder scheduler stopped")
    
    def check_and_send_reminders(self):
        """Check for contests that need reminders and send them"""
        try:
            reminders = self.session.query(Reminder).filter(
                Reminder.sent == False
            ).all()
            
            current_time = datetime.utcnow()
            
            for reminder in reminders:
                contest = reminder.contest
                user = reminder.user
                
                # Calculate time until contest
                time_until_contest = contest.start_time - current_time
                minutes_until = time_until_contest.total_seconds() / 60
                
                # If contest starts within the reminder window
                if minutes_until <= reminder.minutes_before and minutes_until > 0:
                    try:
                        # Send reminder message
                        message = self._format_reminder_message(contest, minutes_until)
                        self.bot.send_message(
                            chat_id=user.telegram_id,
                            text=message,
                            parse_mode="HTML"
                        )
                        
                        # Mark reminder as sent
                        reminder.sent = True
                        self.session.commit()
                        logger.info(f"Reminder sent to user {user.telegram_id} for {contest.name}")
                    
                    except Exception as e:
                        logger.error(f"Error sending reminder: {e}")
                
                # Clean up old contests
                if contest.start_time < current_time - timedelta(hours=1):
                    self.session.delete(reminder)
                    self.session.commit()
        
        except Exception as e:
            logger.error(f"Error in reminder scheduler: {e}")
    
    def _format_reminder_message(self, contest, minutes_until):
        """Format reminder message"""
        minutes_int = int(minutes_until)
        
        message = (
            f"🚀 <b>Contest Reminder!</b>\n\n"
            f"<b>{contest.name}</b>\n"
            f"Platform: {contest.platform}\n"
            f"Starts in: {minutes_int} minutes\n"
        )
        
        if contest.difficulty:
            message += f"Difficulty: {contest.difficulty}\n"
        
        message += f"\n<a href='{contest.url}'>Join Contest</a>"
        
        return message
    
    def add_reminder(self, user_id, contest_id, minutes_before=30):
        """Add a reminder for a user"""
        try:
            # Check if reminder already exists
            existing = self.session.query(Reminder).filter(
                Reminder.user_id == user_id,
                Reminder.contest_id == contest_id
            ).first()
            
            if existing:
                return False  # Already exists
            
            reminder = Reminder(
                user_id=user_id,
                contest_id=contest_id,
                minutes_before=minutes_before,
                sent=False
            )
            self.session.add(reminder)
            self.session.commit()
            logger.info(f"Reminder added for user {user_id}, contest {contest_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding reminder: {e}")
            self.session.rollback()
            return False
    
    def remove_reminder(self, user_id, contest_id):
        """Remove a reminder for a user"""
        try:
            reminder = self.session.query(Reminder).filter(
                Reminder.user_id == user_id,
                Reminder.contest_id == contest_id
            ).first()
            
            if reminder:
                self.session.delete(reminder)
                self.session.commit()
                logger.info(f"Reminder removed for user {user_id}, contest {contest_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing reminder: {e}")
            self.session.rollback()
            return False
    
    def get_user_reminders(self, user_id):
        """Get all reminders for a user"""
        try:
            reminders = self.session.query(Reminder).filter(
                Reminder.user_id == user_id
            ).all()
            return reminders
        except Exception as e:
            logger.error(f"Error fetching user reminders: {e}")
            return []
    
    def close(self):
        """Close database session"""
        self.session.close()
