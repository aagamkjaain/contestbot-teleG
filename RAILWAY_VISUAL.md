# 🎯 RAILWAY DEPLOYMENT - VISUAL GUIDE

**Platform:** railway.app
**Time:** 10 minutes
**Difficulty:** Very Easy (clicks only, no code)

---

## 📋 What You'll Do

```
1. Visit railway.app
   ↓
2. Create account (use GitHub login)
   ↓
3. Connect your telebot GitHub repo
   ↓
4. Add 3 environment variables
   ↓
5. Click "Deploy"
   ↓
6. Watch logs until "Reminder scheduler started"
   ↓
7. Open Telegram and test bot
   ↓
8. 🎉 Bot is LIVE!
```

---

## 🖱️ STEP-BY-STEP CLICKS

### Step 1: Visit Railway Website
```
URL: railway.app
Click: "Start new project"
```

### Step 2: GitHub Login
```
Click: "GitHub" (under sign in options)
Authorize: Allow Railway to access your repos
```

### Step 3: Select Your Repository
```
You'll see a screen asking to pick a repo
Search box: Type "telebot"
Click: Your telebot repository
Click: "Deploy now"
```

**IMPORTANT:** Railway will automatically:
- Detect Python
- Install requirements.txt (5 packages)
- Build Docker image
- Start deployment

⏳ **Wait 1-2 minutes for initial build**

### Step 4: Add Environment Variables

**In Railway Dashboard:**
1. Click the **"Variables"** tab
2. Click **"New Variable"** button
3. Add these ONE BY ONE:

**Variable 1:**
```
Name: TELEGRAM_BOT_TOKEN
Value: 8816657732:AAHS9Zj3zeoQKlpwfMoo35vcx1eiSszvz80
```
Click: Save

**Variable 2:**
```
Name: CLIST_USERNAME
Value: aagamkjain
```
Click: Save

**Variable 3:**
```
Name: CLIST_API_KEY
Value: 11ccd225284ae7d0bba1875e122ae2a3189de53b
```
Click: Save

**Variable 4 (Optional):**
```
Name: TIMEZONE
Value: UTC
```
Click: Save

✅ **All 4 variables saved**

### Step 5: Set Start Command

**In Railway Dashboard:**
1. Click **"Settings"** tab
2. Look for **"Start Command"** field
3. Enter: `python main.py`
4. Click: Save/Enter

### Step 6: Deploy

**In Railway Dashboard:**
1. Click **"Deploy"** button (or it auto-deploys)
2. Go to **"Logs"** tab
3. Watch the build process:

```
[INFO] Building Docker image...
[INFO] Installing dependencies...
[INFO] python main.py
[INFO] Starting Contest Tracker Bot...
[INFO] Reminder scheduler started ✅
```

**When you see "Reminder scheduler started" → Bot is LIVE!** 🎉

### Step 7: Get Your Bot URL

**In Railway Dashboard:**
1. Click **"Deploy"** tab
2. Copy the **Railway URL**
3. This is your bot's public URL

---

## 🧪 TESTING ON TELEGRAM

### Find Your Bot

**Option A: Direct URL**
```
https://t.me/your_bot_username
```

**Option B: Search Telegram**
1. Open Telegram
2. Search for your bot name
3. Click the bot

### Test Commands

**Send these commands one-by-one:**

#### Command 1: /start
```
You type: /start
Bot responds: "🚀 Welcome to Contest Tracker!" 
             [Feature list]
Expected: ✅ Welcome message
```

#### Command 2: /subscribe
```
You type: /subscribe Codeforces
Bot responds: "✅ Subscribed to Codeforces!"
Expected: ✅ Confirmation message
```

#### Command 3: /upcoming
```
You type: /upcoming
Bot responds: [Waits 3-5 seconds]
             "📅 Upcoming Contests (Next 7 Days):"
             [List of contests]
Expected: ✅ Contest list from CLIST API
```

#### Command 4: /weekly
```
You type: /weekly
Bot responds: "📊 Weekly Digest"
             "Total Contests: X"
             [Stats by platform]
Expected: ✅ Statistics displayed
```

#### Command 5: /help
```
You type: /help
Bot responds: "🤖 Contest Tracker Bot - Help"
             [All commands listed]
Expected: ✅ Help message
```

#### Command 6: /calendar
```
You type: /calendar
Bot responds: "📅 Calendar export feature coming soon!"
Expected: ✅ Coming soon message
```

---

## 📊 Expected Timeline

```
0:00 - Start deployment
0:30 - Build complete, bot starting
1:00 - "Reminder scheduler started" appears in logs ✅
2:00 - Test /start command
2:15 - Test /subscribe command
2:30 - Test /upcoming command (waits for API)
3:00 - All tests pass ✅
       Bot is LIVE and working! 🎉
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: "Deployment Failed"
**Check:**
- Railway logs for error message
- Common: Missing environment variables
- Solution: Verify all 4 variables are added correctly

**Action:** Add variables again, click "Redeploy"

### Issue 2: Bot Doesn't Respond
**Check:**
- Has 30 seconds passed? (first startup takes time)
- Railway logs: Does it show "Reminder scheduler started"?
- TELEGRAM_BOT_TOKEN: Is it exactly correct? (copy from .env)

**Action:** 
1. Wait 30 seconds
2. Try /start again
3. Check Railway logs for errors

### Issue 3: /upcoming Shows No Contests
**Check:**
- Did you /subscribe to a platform first?
- Are CLIST credentials correct?
- Are you subscribed to Codeforces? (test command uses that)

**Action:** 
1. Try /subscribe Codeforces first
2. Then /upcoming
3. Wait 3-5 seconds for API response

### Issue 4: "Invalid Token"
**Check:**
- Copy token from your .env file exactly
- No extra spaces or characters
- Verify it starts with "8816657732:"

**Action:**
1. Copy entire token from .env
2. Remove any spaces
3. Paste into Railway variable
4. Redeploy

### Issue 5: Reminders Not Sending
**Check:**
- Scheduler checks every 60 seconds
- Is bot running? (logs show "Reminder scheduler started"?)
- Are there any contests in DB?

**Action:**
1. Wait 60+ seconds
2. Run /upcoming to populate DB
3. Wait another 60 seconds
4. Check logs for "Reminder sent"

---

## 🔍 How to Monitor Logs

**In Railway Dashboard:**

1. Click **"Logs"** tab
2. Real-time logs appear
3. Look for:
   - ✅ "Starting Contest Tracker Bot..."
   - ✅ "Reminder scheduler started"
   - ❌ Red errors (if any)
   - 📍 User commands
   - 🔄 API calls to CLIST

**Example Good Log:**
```
2026-06-11 10:30:45 - Start log
2026-06-11 10:30:47 - Loading configuration
2026-06-11 10:30:48 - Starting Contest Tracker Bot...
2026-06-11 10:30:49 - Reminder scheduler started ✅
2026-06-11 10:30:50 - Bot ready and waiting for messages
[User sends /start]
2026-06-11 10:31:15 - /start command from user 123456
2026-06-11 10:31:15 - User registered
2026-06-11 10:31:16 - Welcome message sent
```

**Example Problem Log:**
```
Error: TELEGRAM_BOT_TOKEN is not set in .env file ❌
[This means: environment variable not added]
```

---

## 💾 Important Files in Railway

Railway will use these files:
```
requirements.txt   ← Installs Python packages ✅
bot.py            ← Main bot code ✅
main.py           ← Entry point ✅
[All other files]  ← Available to bot ✅
```

✅ **All your files are there!**

---

## 🎮 Testing Checklist

After bot is live:

```
Telegram Testing:
  [ ] /start works
  [ ] /help works
  [ ] /subscribe Codeforces works
  [ ] /upcoming shows contests (wait 3-5s)
  [ ] /weekly shows statistics
  [ ] /subscribe LeetCode works
  [ ] /upcoming shows both platforms (wait 3-5s)
  [ ] /unsubscribe Codeforces works
  [ ] /upcoming shows only LeetCode (wait 3-5s)
  [ ] /weekly shows updated counts
  [ ] /calendar shows message
  [ ] /reminder shows info
  [ ] Wait 60+ seconds
  [ ] Check for reminder message (if contest starting soon)

Expected Results:
  ✅ All commands respond
  ✅ /upcoming fetches contests (3-5 sec delay is normal)
  ✅ /weekly shows correct stats
  ✅ Platform filtering works
  ✅ Reminders work (after 60+ sec wait)
  ✅ No error messages

If all ✅, your bot is PERFECT! 🎉
```

---

## 🚀 GO LIVE NOW!

### Your Deployment Checklist:

**Before Starting:**
- [x] Code is ready (already built)
- [x] Git is up to date (already pushed)
- [x] .env has credentials (already configured)

**During Deployment:**
- [ ] Open railway.app
- [ ] Create account (GitHub login)
- [ ] Select telebot repo
- [ ] Add 4 environment variables
- [ ] Set start command: python main.py
- [ ] Click Deploy
- [ ] Wait for logs to show "Reminder scheduler started"

**After Deployment:**
- [ ] Open Telegram
- [ ] Find your bot
- [ ] Send /start
- [ ] Verify all commands work
- [ ] Test /upcoming (wait 3-5 sec)
- [ ] Celebrate! 🎉

---

## 📞 Quick Help

**Question:** How long until bot is live?
**Answer:** 2-3 minutes from clicking Deploy

**Question:** How do I see what's happening?
**Answer:** Watch the Logs tab in Railway dashboard

**Question:** What if something fails?
**Answer:** Check logs for error message, use troubleshooting section above

**Question:** Can I update the bot later?
**Answer:** Yes! Just push to GitHub, Railway auto-redeploys

**Question:** Is the bot always on?
**Answer:** Yes! Railway keeps it running 24/7

---

## 🎊 You're Ready!

Everything is prepared. 

Go to **railway.app** and deploy your bot right now! 

It will take ~10 minutes and your bot will be LIVE.

Then test it on Telegram and celebrate! 🎉

---

**Good luck! Your Contest Tracker Bot is about to go live!** 🚀
