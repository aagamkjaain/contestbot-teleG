import requests
from datetime import datetime, timedelta
from config import CLIST_USERNAME, CLIST_API_KEY, CLIST_BASE_URL
from database import Session, Contest, get_session


class ContestService:
    """Service to fetch contests from CLIST API"""
    
    def __init__(self):
        self.username = CLIST_USERNAME
        self.api_key = CLIST_API_KEY
        self.base_url = CLIST_BASE_URL
        self.session = get_session()
    
    def _get_headers(self):
        """Get authorization headers for CLIST API"""
        return {
            "Authorization": f"ApiKey {self.username}:{self.api_key}"
        }
    
    def get_upcoming_contests(self, days_ahead=30, limit=100):
        """
        Fetch upcoming contests from CLIST API
        
        Args:
            days_ahead: Number of days to look ahead
            limit: Maximum number of contests to fetch
            
        Returns:
            List of contest dictionaries
        """
        try:
            params = {
                "upcoming": "true",
                "format": "json",
                "limit": limit,
                "order_by": "start"
            }
            
            headers = self._get_headers()
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            contests = []
            
            if "objects" in data:
                for contest in data["objects"]:
                    try:
                        start_time = datetime.fromisoformat(contest["start"].replace("Z", "+00:00"))
                        
                        # Filter by days_ahead
                        if start_time > datetime.now(start_time.tzinfo) + timedelta(days=days_ahead):
                            continue
                        
                        contest_dict = {
                            "clist_id": contest.get("id"),
                            "name": contest.get("event"),
                            "platform": contest.get("resource", {}).get("name", "Unknown"),
                            "start": start_time.isoformat(),
                            "url": contest.get("url", ""),
                            "duration": contest.get("duration"),
                            "difficulty": self._estimate_difficulty(contest.get("resource", {}).get("name", ""))
                        }
                        contests.append(contest_dict)
                    except Exception as e:
                        print(f"Error processing contest: {e}")
                        continue
            
            return contests
        
        except requests.RequestException as e:
            print(f"Error fetching contests from CLIST: {e}")
            return []
    
    def _estimate_difficulty(self, platform):
        """Estimate difficulty based on platform"""
        easy_platforms = ["LeetCode", "HackerRank"]
        hard_platforms = ["TopCoder", "AtCoder"]
        
        if platform in easy_platforms:
            return "Easy"
        elif platform in hard_platforms:
            return "Hard"
        else:
            return "Intermediate"
    
    def save_contests(self, contests):
        """Save fetched contests to database"""
        try:
            for contest_data in contests:
                # Check if contest already exists
                existing = self.session.query(Contest).filter(
                    Contest.clist_id == contest_data["clist_id"]
                ).first()
                
                if not existing:
                    start_time = datetime.fromisoformat(contest_data["start"])
                    contest = Contest(
                        clist_id=contest_data["clist_id"],
                        name=contest_data["name"],
                        platform=contest_data["platform"],
                        start_time=start_time,
                        url=contest_data["url"],
                        duration=contest_data.get("duration"),
                        difficulty=contest_data.get("difficulty")
                    )
                    self.session.add(contest)
            
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error saving contests: {e}")
            self.session.rollback()
            return False
    
    def get_contests_for_user(self, user_id, days_ahead=7):
        """Get contests filtered by user's subscriptions"""
        from database import User
        
        try:
            user = self.session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                return []
            
            # Get user's subscribed platforms
            subscribed_platforms = [
                sub.platform for sub in user.subscriptions if sub.subscribed
            ]
            
            if not subscribed_platforms:
                # If no subscriptions, return all platforms
                subscribed_platforms = None
            
            # Query contests
            query = self.session.query(Contest).filter(
                Contest.start_time >= datetime.utcnow(),
                Contest.start_time <= datetime.utcnow() + timedelta(days=days_ahead)
            ).order_by(Contest.start_time)
            
            if subscribed_platforms:
                query = query.filter(Contest.platform.in_(subscribed_platforms))
            
            return query.all()
        except Exception as e:
            print(f"Error fetching user contests: {e}")
            return []
    
    def close(self):
        """Close database session"""
        self.session.close()
