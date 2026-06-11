# Contest Tracker Bot - Endpoints & Deployment Plan

## 📋 Bot Endpoints (Telegram Commands)

### 1. `/start`
**Type:** Command Handler
**Purpose:** Register new users and show welcome message
**Response:** 
- Welcome message with feature list
- User is registered in database
- Can be called multiple times safely

**Test:**
```
/start
```

---

### 2. `/upcoming`
**Type:** Command Handler
**Purpose:** Show next 10 upcoming contests in 7 days
**Features:**
- Fetches from CLIST API
- Saves to database
- Filters by user's platform subscriptions
- Shows: Contest name, platform, start time, difficulty, link

**Test:**
```
/upcoming
```

---

### 3. `/subscribe <platform>`
**Type:** Command Handler with Arguments
**Purpose:** Subscribe to contests on a specific platform
**Supported Platforms:**
- Codeforces
- LeetCode
- CodeChef
- AtCoder
- TopCoder
- HackerEarth
- HackerRank

**Test:**
```
/subscribe Codeforces
/subscribe LeetCode
```

---

### 4. `/unsubscribe <platform>`
**Type:** Command Handler with Arguments
**Purpose:** Unsubscribe from a platform
**Test:**
```
/unsubscribe Codeforces
```

---

### 5. `/reminder`
**Type:** Command Handler
**Purpose:** Show reminder settings information
**Features:**
- Default: 30 minutes before contest
- Auto-sends reminders via background scheduler
**Test:**
```
/reminder
```

---

### 6. `/help`
**Type:** Command Handler
**Purpose:** Display all available commands and platforms
**Response:** List of all commands with descriptions
**Test:**
```
/help
```

---

### 7. `/weekly`
**Type:** Command Handler
**Purpose:** Show weekly digest statistics (next 7 days)
**Features:**
- Total contest count
- Breakdown by platform
- Breakdown by difficulty
**Test:**
```
/weekly
```

---

### 8. `/calendar`
**Type:** Command Handler
**Purpose:** Export contests to calendar format (ICS)
**Features:** 
- Generates .ics file format
- Ready for Google Calendar import
- Currently returns "coming soon" message (feature ready in utils.py)
**Test:**
```
/calendar
```

---

## 🔄 Background Services (Non-Command)

### Reminder Scheduler
**Type:** Background Job (APScheduler)
**Frequency:** Every 60 seconds
**Purpose:** 
- Check for contests starting within reminder window
- Send automated reminder messages to users
- Mark reminders as sent
- Clean up old contests

**How it works:**
1. Runs continuously in background
2. Checks database for unsent reminders
3. Calculates time until contest
4. If within reminder window, sends message
5. Updates reminder status

---

## 📊 API Integration Points

### CLIST API
**Endpoint:** `https://clist.by/api/v4/contest/`
**Authentication:** ApiKey {USERNAME}:{API_KEY}
**Parameters:**
- `upcoming`: true (fetch upcoming contests)
- `format`: json
- `limit`: 100 (number of contests)
- `order_by`: start (sort by start time)

**Response:** JSON with contest objects including:
- id (clist_id)
- event (contest name)
- resource.name (platform)
- start (ISO datetime)
- url (contest link)
- duration (seconds)

---

## 🛠️ Architecture for Deployment

### Current Setup (Local - Long Polling)
```
User → Telegram → Telegram API → Bot (Polling) → CLIST API
                                    ↓
                                Database (SQLite)
```

### Deployment Architecture
```
User → Telegram → Telegram API → Railway/Render/Fly.io
                                    ↓
                                  Bot Container
                                    ↓
                            APScheduler (Reminders)
                                    ↓
                              SQLite/PostgreSQL
                                    ↓
                              CLIST API
```

---

## 🚀 Deployment Options

### Option 1: Railway ⭐ (Easiest)
**Pros:**
- Very easy setup
- Free tier available ($5/month)
- GitHub integration
- Environment variables UI
- Built-in database support (PostgreSQL optional)

**Steps:**
1. Push code to GitHub
2. Connect GitHub to Railway
3. Create new project from repo
4. Add environment variables:
   - TELEGRAM_BOT_TOKEN
   - CLIST_USERNAME
   - CLIST_API_KEY
   - DATABASE_URL (optional, uses SQLite on disk)
5. Deploy (Railway handles Docker automatically)

**Cost:** $5/month or free tier
**Domain:** yourapp.up.railway.app (optional)

---

### Option 2: Render
**Pros:**
- Free tier with 750 hours/month
- Automatic deployment from GitHub
- PostgreSQL database included
- Email notifications

**Steps:**
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repo
4. Add environment variables
5. Deploy

**Cost:** Free (if under 750 hours/month)
**Limitation:** Service sleeps after 15 minutes of inactivity (may need paid tier for 24/7)

---

### Option 3: Fly.io
**Pros:**
- Free tier available
- Global deployment
- PostgreSQL included
- Always-on support

**Steps:**
1. Install Fly CLI
2. Run `flyctl launch`
3. Add environment variables to fly.toml
4. Deploy with `flyctl deploy`

**Cost:** Free to start
**Limitation:** Free tier has resource limits

---

## 📦 Deployment Checklist

### Pre-Deployment
- [ ] Push all code to GitHub (already done ✅)
- [ ] .env is NOT committed (in .gitignore ✅)
- [ ] requirements.txt is up to date ✅
- [ ] Database initializes on first run ✅
- [ ] All commands tested locally
- [ ] Bot token is valid
- [ ] CLIST credentials are valid

### Deployment Platform Selection
- [ ] Choose platform (Railway recommended for ease)
- [ ] Create account on chosen platform
- [ ] Connect GitHub account
- [ ] Create new project/app

### Environment Setup
- [ ] Add TELEGRAM_BOT_TOKEN
- [ ] Add CLIST_USERNAME
- [ ] Add CLIST_API_KEY
- [ ] Set DATABASE_URL (if using external database)
- [ ] Set TIMEZONE (default: UTC)

### Post-Deployment
- [ ] Verify bot is running
- [ ] Test /start command
- [ ] Test /upcoming command
- [ ] Verify reminders are working
- [ ] Check logs for errors
- [ ] Monitor resource usage

---

## 🔧 Deployment Configuration Files Needed

### For Railway/Render (Auto-detected):
No additional files needed! The platforms auto-detect Python and install from requirements.txt

### Optional - For Fly.io (fly.toml):
```toml
app = "contest-tracker"
kill_signal = "SIGINT"
kill_timeout = 5

[env]
  PYTHON_VERSION = "3.11"

[processes]
  web = "python main.py"

[[services]]
  protocol = "tcp"
  internal_port = 8080
  processes = ["web"]
  auto_start = true
  auto_stop = true
```

### Optional - Dockerfile (if needed):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

---

## 🎯 Performance Metrics

### Expected Resource Usage:
- **CPU:** Minimal (only processes when bot receives messages)
- **Memory:** ~50-100 MB (with scheduler running)
- **Disk:** ~5-10 MB (SQLite database)
- **Network:** Polling mode = constant low traffic

### Polling vs Webhooks:
- **Current:** Long polling (checks Telegram every few seconds)
- **Polling Pros:** No server setup needed, works behind any firewall
- **Polling Cons:** Slightly more resource usage
- **For Deployment:** Polling works fine, no changes needed

---

## 🔐 Security Considerations

### Secrets Management ✅
- Bot token stored in environment variables
- API keys stored in environment variables
- .env file is .gitignored (not in repo)
- Database credentials optional (SQLite is local)

### API Limits
- CLIST API: ~1000 requests/day (plenty)
- Telegram Bot: Unlimited
- APScheduler: Every 60 seconds = 1,440 checks/day

### Best Practices ✅
- All environment variables use env vars
- No hardcoded secrets in code
- Database auto-initializes on startup
- Error handling for API failures

---

## 📈 Scaling Considerations (Future)

**If bot grows to many users:**

1. **Database Upgrade**
   - Switch from SQLite to PostgreSQL
   - Change DATABASE_URL in .env
   - No code changes needed (SQLAlchemy handles it)

2. **Caching**
   - Cache contest list (update every 1 hour)
   - Reduce API calls to CLIST

3. **Load Balancing**
   - Run multiple bot instances
   - Use message queue (Redis) for reminders
   - Distribute scheduler across instances

4. **Monitoring**
   - Add error tracking (Sentry)
   - Add logging aggregation (Datadog)
   - Monitor resource usage

---

## 🧪 Testing Deployment

### Local Testing (Before Deployment)
```bash
# Test configuration
python -c "from config import *; print('Config OK')"

# Test database
python -c "from database import init_db; init_db(); print('DB OK')"

# Test CLIST API
python -c "from contest_service import ContestService; s = ContestService(); print(len(s.get_upcoming_contests())); print('API OK')"

# Run bot
python main.py
```

### Post-Deployment Testing
1. Find bot on Telegram
2. Send `/start` - verify response
3. Send `/upcoming` - verify contests load
4. Send `/subscribe Codeforces` - verify subscription
5. Send `/weekly` - verify digest shows
6. Wait 2 minutes, verify reminders work
7. Check platform logs for errors

---

## 📊 Deployment Decision Matrix

| Factor | Railway | Render | Fly.io |
|--------|---------|--------|--------|
| Setup Time | 5 min | 10 min | 15 min |
| Cost | $5/mo | Free/mo* | Free/mo* |
| Ease | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| GitHub Integration | Native | Native | CLI |
| Uptime Guarantee | 99.9% | 99% | 99.5% |
| Always-On | Yes | No** | Yes |
| Support | Good | Good | Excellent |

*Free tier has restrictions
**Requires paid plan for 24/7

---

## ✅ Recommendation: Deploy on Railway

**Why Railway?**
1. ✅ Easiest setup (5 minutes)
2. ✅ GitHub integration is seamless
3. ✅ $5/month is very affordable
4. ✅ Always-on (no sleep mode)
5. ✅ Good documentation
6. ✅ Easy environment variable management
7. ✅ Scales well as bot grows

**Next Steps:**
1. Go to railway.app
2. Create account (connect GitHub)
3. Create new project from your telebot GitHub repo
4. Add 3 environment variables
5. Deploy (1 click!)
6. Test bot

---

## 🎯 Summary

**Bot Endpoints:** 8 commands + 1 background service
**Current Architecture:** Python + SQLite + APScheduler + Telegram API
**Ready for Deployment:** YES ✅
**Recommended Platform:** Railway
**Estimated Setup Time:** ~15 minutes
**Monthly Cost:** $5 (Railway) or Free (Render - with limitations)

