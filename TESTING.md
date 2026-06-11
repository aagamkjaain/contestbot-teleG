# Testing Checklist for Contest Tracker Bot

## Pre-Testing Setup

- [ ] Create `.env` file with valid credentials:
  - [ ] Valid TELEGRAM_BOT_TOKEN (from @BotFather)
  - [ ] Valid CLIST_USERNAME and CLIST_API_KEY (from clist.by)

- [ ] Install Python 3.8+ locally

- [ ] Create virtual environment:
  ```bash
  python -m venv venv
  venv\Scripts\activate  # Windows
  # or
  source venv/bin/activate  # macOS/Linux
  ```

- [ ] Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Initialize database:
  ```bash
  python -c "from database import init_db; init_db()"
  ```

## Unit Tests to Perform

### 1. Configuration Loading
- [ ] Test that config.py loads all environment variables
- [ ] Test that validation fails if TELEGRAM_BOT_TOKEN is missing
- [ ] Test that validation fails if CLIST credentials are missing

### 2. Database Tests
- [ ] Test database initialization creates all tables
- [ ] Test User model creation and retrieval
- [ ] Test Contest model creation and retrieval
- [ ] Test Reminder model relationships
- [ ] Test Subscription model creation

### 3. Contest Service Tests
```python
# In Python shell
from contest_service import ContestService
service = ContestService()

# Test API connection
contests = service.get_upcoming_contests()
print(f"Fetched {len(contests)} contests")

# Test saving to database
service.save_contests(contests)

# Test filtering by user (after user is registered)
user_contests = service.get_contests_for_user(123456789)
print(f"User has {len(user_contests)} contests")
```

### 4. Bot Command Tests
Run the bot and test each command:

1. **Test /start**
   - [ ] Bot responds with welcome message
   - [ ] User is registered in database
   - [ ] Can run /start multiple times without errors

2. **Test /upcoming**
   - [ ] Shows list of upcoming contests
   - [ ] Displays contest name, platform, start time, difficulty
   - [ ] Includes link to contest
   - [ ] Shows message if no contests found

3. **Test /subscribe and /unsubscribe**
   ```
   /subscribe Codeforces
   /subscribe LeetCode
   /unsubscribe Codeforces
   /upcoming  # Should only show LeetCode contests
   ```
   - [ ] Subscriptions are saved to database
   - [ ] Upcoming contests are filtered correctly
   - [ ] Can subscribe to same platform multiple times (idempotent)

4. **Test /reminder**
   - [ ] Shows reminder information message

5. **Test /weekly**
   - [ ] Shows weekly digest statistics
   - [ ] Counts contests by platform correctly
   - [ ] Shows total contest count

6. **Test /help**
   - [ ] Displays all available commands
   - [ ] Shows platform list

7. **Test /calendar**
   - [ ] Returns success message (feature notice)

### 5. Scheduler Tests
- [ ] Background scheduler starts without errors
- [ ] Scheduler checks for reminders every 60 seconds
- [ ] Verify in logs: "Reminder scheduler started"

### 6. Integration Tests

1. **Full User Flow**
   ```
   /start                      # Register user
   /subscribe Codeforces       # Subscribe to platform
   /upcoming                   # View contests
   /weekly                     # Get weekly digest
   /help                       # View help
   ```
   - [ ] All commands work in sequence
   - [ ] Data is persisted in database
   - [ ] No errors in logs

2. **Reminder System**
   - [ ] Add a reminder for a contest
   - [ ] Verify reminder appears in database
   - [ ] Scheduler sends reminder at correct time
   - [ ] Reminder is marked as sent

3. **Database Persistence**
   - [ ] Stop bot, restart bot
   - [ ] User data still exists
   - [ ] Contests still in database
   - [ ] Subscriptions still active

## Performance Tests

- [ ] Bot responds to commands within 2 seconds
- [ ] /upcoming command completes within 3 seconds
- [ ] API calls complete within timeout (10 seconds)
- [ ] Database operations are fast (< 1 second)

## Error Handling Tests

- [ ] Test with invalid CLIST credentials
  - [ ] Should log error
  - [ ] Should return empty contest list
  - [ ] Bot should not crash

- [ ] Test with invalid Telegram token
  - [ ] Should fail with clear error message on startup

- [ ] Test with corrupted .env file
  - [ ] Should fail gracefully with error message

- [ ] Test network timeout
  - [ ] Bot should handle network errors gracefully
  - [ ] Should log timeout errors

## Database Tests

- [ ] Check contests.db is created in project root
- [ ] Run SQL queries to verify data:
  ```sql
  SELECT COUNT(*) FROM users;
  SELECT COUNT(*) FROM contests;
  SELECT COUNT(*) FROM reminders;
  SELECT COUNT(*) FROM subscriptions;
  ```

## Logging Tests

- [ ] Check that logs appear in terminal
- [ ] Verify format: `timestamp - name - level - message`
- [ ] Errors are logged with traceback
- [ ] Info messages appear on startup/commands

## Final Checklist

- [ ] All commands work without errors
- [ ] Database contains expected data
- [ ] Reminders are sent at correct times
- [ ] User data persists across restarts
- [ ] No unhandled exceptions in logs
- [ ] Bot can be stopped cleanly with Ctrl+C
- [ ] All requirements.txt packages are installed

## Testing Notes

```bash
# Run bot
python main.py

# In another terminal, check database
sqlite3 contests.db
sqlite> SELECT * FROM users;
sqlite> SELECT * FROM contests LIMIT 5;
sqlite> .tables
sqlite> .quit
```

## Ready for Deployment ✅
Once all tests pass, the bot is ready to deploy to Railway/Render/Fly.io
