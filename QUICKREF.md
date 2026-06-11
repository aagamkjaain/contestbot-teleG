# 📱 Bot Commands - Quick Reference Card

## Print This Card & Keep It Handy! 📋

---

## 8 Main Commands

### 1. `/start`
Registers you and shows welcome message
```
/start
→ Welcome! [Feature list]
```

### 2. `/upcoming`
Shows next 10 contests (7 days)
```
/upcoming
→ [List of contests with links]
```

### 3. `/subscribe <platform>`
Subscribe to get contests from that platform
```
/subscribe Codeforces
→ ✅ Subscribed to Codeforces!
```

### 4. `/unsubscribe <platform>`
Stop getting contests from that platform
```
/unsubscribe Codeforces
→ ✅ Unsubscribed from Codeforces
```

### 5. `/reminder`
Shows reminder settings info
```
/reminder
→ Reminder set 30 mins before contest
```

### 6. `/weekly`
Shows this week's contest stats
```
/weekly
→ [Stats by platform & difficulty]
```

### 7. `/help`
Shows all commands & platforms
```
/help
→ [List of all commands]
```

### 8. `/calendar`
Export contests to Google Calendar
```
/calendar
→ Coming soon! [Message]
```

---

## Available Platforms

Choose any of these with `/subscribe`:
- Codeforces
- LeetCode
- CodeChef
- AtCoder
- TopCoder
- HackerEarth
- HackerRank

---

## Background Service

**Reminder System** ⏰
- Runs every 60 seconds
- Sends message 30 min before contest
- Works automatically (no command needed)

---

## Example Workflow

```
1. /start
   → Bot registers you

2. /subscribe Codeforces
   → Subscribe to Codeforces

3. /subscribe LeetCode
   → Subscribe to LeetCode

4. /upcoming
   → Shows Codeforces + LeetCode contests

5. /weekly
   → Shows stats (2 platform = X contests)

6. [Wait for contests]
   → Bot sends reminders 30 min before!
```

---

## Command Response Times

| Command | Time |
|---------|------|
| /start | <1 sec |
| /upcoming | 3-5 sec |
| /subscribe | <1 sec |
| /unsubscribe | <1 sec |
| /reminder | <1 sec |
| /weekly | <1 sec |
| /help | <1 sec |
| /calendar | <1 sec |

---

## Supported Features

✅ Track contests from 7+ platforms
✅ Platform filtering (subscribe/unsubscribe)
✅ Automatic reminders (30 min before)
✅ Weekly statistics
✅ Contest difficulty ratings
✅ Direct links to contests
✅ Persistent user data
✅ 24/7 operation

---

## Error Messages

| Error | Solution |
|-------|----------|
| "Usage: /subscribe <platform>" | Provide platform name |
| "Unsubscribed from X" | Subscribe again with `/subscribe` |
| "No contests found" | Subscribe to at least one platform |

---

## Keyboard Shortcuts

| Key | Command |
|-----|---------|
| Type `/` | Shows all commands |
| Type `/u` | Auto-complete /upcoming |
| Type `/s` | Auto-complete /subscribe |

---

## FAQ

**Q: How often does the bot check?**
A: Reminders check every 60 seconds

**Q: How early can I get reminders?**
A: Default 30 minutes before contest

**Q: Can I change reminder time?**
A: Feature coming soon (currently 30 min default)

**Q: Does the bot work 24/7?**
A: Yes! Deployed on Railway (always running)

**Q: Can I use multiple platforms?**
A: Yes! Subscribe to as many as you want

**Q: What if I don't subscribe?**
A: `/upcoming` shows all contests by default

**Q: Can I export to Google Calendar?**
A: Coming soon (feature ready)

---

## Reminder System Details

When you use `/upcoming`, the bot:
1. Fetches contests from CLIST API
2. Saves to database (so you don't lose them)
3. Filters by your subscriptions
4. Shows top 10 contests

Then every 60 seconds:
1. Scheduler checks if contest is starting soon
2. If within 30 minutes: **SENDS REMINDER**
3. Message includes contest link
4. Marks reminder as sent

---

## Tips & Tricks

💡 **Tip 1:** Subscribe to multiple platforms
```
/subscribe Codeforces
/subscribe LeetCode
/subscribe CodeChef
```

💡 **Tip 2:** Check weekly stats
```
/weekly
```
Shows all platforms + counts

💡 **Tip 3:** Help is always available
```
/help
```
Shows commands and platforms

💡 **Tip 4:** Set phone reminder
Use system notification for /upcoming (or /weekly)

---

## Architecture at a Glance

```
You → Telegram → Bot (Railway) → CLIST API
                 ↓
            Database
          + Scheduler
```

---

## Tech Stack (For Developers)

- **Language:** Python 3.8+
- **Bot Framework:** python-telegram-bot 21.0
- **Database:** SQLAlchemy + SQLite
- **Scheduler:** APScheduler
- **API:** CLIST.by REST API
- **Deployment:** Railway, Render, or Fly.io

---

## Support Resources

- 📖 **README.md** - Full documentation
- 🚀 **QUICK_DEPLOY.md** - How to deploy
- 🔌 **ENDPOINTS.md** - API details
- ✅ **TESTING.md** - Testing guide
- 📋 **DEPLOYMENT.md** - Architecture

---

## Keep This Handy!

Print this page and keep it next to your desk:
- Shows all 8 commands
- Response times
- Supported platforms
- Common errors
- Pro tips

---

**Bot Status:** ✅ RUNNING
**Last Updated:** June 11, 2026
**Version:** 1.0.0 Release

