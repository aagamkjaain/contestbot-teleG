"""
Utility functions for Contest Tracker Bot
"""

from datetime import datetime
from database import get_session, User, Contest


def generate_ics_calendar(user_id):
    """
    Generate an ICS (iCalendar) file for contests
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        ICS content as string
    """
    session = get_session()
    
    try:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            return None
        
        # Get all upcoming contests for the user
        from contest_service import ContestService
        service = ContestService()
        contests = service.get_contests_for_user(user_id, days_ahead=365)
        
        # Create ICS header
        ics_content = (
            "BEGIN:VCALENDAR\n"
            "VERSION:2.0\n"
            "PRODID:-//Contest Tracker Bot//EN\n"
            "CALSCALE:GREGORIAN\n"
            "METHOD:PUBLISH\n"
            "X-WR-CALNAME:Programming Contests\n"
            "X-WR-TIMEZONE:UTC\n"
            "BEGIN:VTIMEZONE\n"
            "TZID:UTC\n"
            "BEGIN:STANDARD\n"
            "DTSTART:19700101T000000Z\n"
            "TZOFFSETFROM:+0000\n"
            "TZOFFSETTO:+0000\n"
            "END:STANDARD\n"
            "END:VTIMEZONE\n"
        )
        
        # Add events
        for contest in contests:
            start_time = contest.start_time.isoformat().replace('-', '').replace(':', '')
            
            # Calculate end time (start + duration if available, else +2 hours)
            if contest.duration:
                duration_hours = contest.duration / 3600
            else:
                duration_hours = 2
            
            end_time = (contest.start_time.__class__.fromtimestamp(
                contest.start_time.timestamp() + (duration_hours * 3600)
            )).isoformat().replace('-', '').replace(':', '')
            
            # Escape special characters
            title = contest.name.replace('\\', '\\\\').replace(',', '\\,').replace(';', '\\;')
            
            ics_content += (
                "BEGIN:VEVENT\n"
                f"UID:{contest.clist_id}@contest-tracker\n"
                f"DTSTAMP:{datetime.utcnow().isoformat()}Z\n"
                f"DTSTART;TZID=UTC:{start_time}Z\n"
                f"DTEND;TZID=UTC:{end_time}Z\n"
                f"SUMMARY:{title}\n"
                f"DESCRIPTION:Platform: {contest.platform}\\nDifficulty: {contest.difficulty or 'N/A'}\n"
                f"URL:{contest.url}\n"
                "END:VEVENT\n"
            )
        
        ics_content += "END:VCALENDAR\n"
        
        session.close()
        return ics_content
    
    except Exception as e:
        print(f"Error generating ICS calendar: {e}")
        session.close()
        return None


def get_weekly_stats(user_id):
    """
    Get statistics for contests in the next 7 days
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Dictionary with contest statistics
    """
    session = get_session()
    
    try:
        from contest_service import ContestService
        service = ContestService()
        contests = service.get_contests_for_user(user_id, days_ahead=7)
        
        stats = {
            "total": len(contests),
            "by_platform": {},
            "by_difficulty": {},
            "contests": []
        }
        
        for contest in contests:
            # Count by platform
            platform = contest.platform
            stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1
            
            # Count by difficulty
            difficulty = contest.difficulty or "Unknown"
            stats["by_difficulty"][difficulty] = stats["by_difficulty"].get(difficulty, 0) + 1
            
            # Add contest details
            stats["contests"].append({
                "name": contest.name,
                "platform": platform,
                "start": contest.start_time.isoformat(),
                "difficulty": difficulty
            })
        
        session.close()
        return stats
    
    except Exception as e:
        print(f"Error getting weekly stats: {e}")
        session.close()
        return None


def format_contest_message(contest):
    """Format a single contest for display"""
    start_time = contest.start_time.strftime("%Y-%m-%d %H:%M UTC")
    
    message = (
        f"<b>{contest.name}</b>\n"
        f"Platform: {contest.platform}\n"
        f"Start: {start_time}\n"
    )
    
    if contest.difficulty:
        message += f"Difficulty: {contest.difficulty}\n"
    
    message += f"<a href='{contest.url}'>Join Contest</a>"
    
    return message


def format_weekly_digest_message(stats):
    """Format weekly digest statistics"""
    message = f"📊 <b>Weekly Digest</b>\n\n"
    message += f"<b>Total Contests: {stats['total']}</b>\n\n"
    
    if stats['by_platform']:
        message += "<b>By Platform:</b>\n"
        for platform, count in sorted(stats['by_platform'].items()):
            message += f"  {platform}: {count}\n"
    
    if stats['by_difficulty']:
        message += "\n<b>By Difficulty:</b>\n"
        for difficulty, count in sorted(stats['by_difficulty'].items()):
            message += f"  {difficulty}: {count}\n"
    
    return message


def cleanup_old_contests(days=7):
    """Clean up contests older than specified days"""
    from datetime import datetime, timedelta
    
    session = get_session()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old contests
        deleted = session.query(Contest).filter(
            Contest.start_time < cutoff_date
        ).delete()
        
        session.commit()
        print(f"Deleted {deleted} old contests")
        
        session.close()
        return deleted
    
    except Exception as e:
        print(f"Error cleaning up contests: {e}")
        session.rollback()
        session.close()
        return 0
