# 🚀 RAILWAY DEPLOYMENT - STEP-BY-STEP GUIDE

**Estimated Time:** 10 minutes
**Status:** Ready to deploy ✅

---

## Step 1: Prepare Your Repository (2 minutes) ✅

### Verify Git Status
```bash
cd k:\telebot
git status
```

**Expected Output:**
```
On branch main
nothing to commit, working tree clean
```

✅ **Your code is already committed and pushed!**

Let me verify what's in your repo:

---

## Step 2: Create Railway Account (3 minutes)

### Go to Railway
1. Open browser: **railway.app**
2. Click "Start new project"
3. Click "Deploy from GitHub repo"
4. Authorize Railway to access GitHub
5. Search for your "telebot" repo
6. Select it
7. Click "Deploy now"

✅ **Railway will auto-detect Python and install requirements.txt**

---

## Step 3: Add Environment Variables (2 minutes)

In Railway dashboard after deployment starts:

1. Go to **Variables** tab
2. Add these variables:

```
TELEGRAM_BOT_TOKEN = 8816657732:AAHS9Zj3zeoQKlpwfMoo35vcx1eiSszvz80
CLIST_USERNAME = aagamkjain
CLIST_API_KEY = 11ccd225284ae7d0bba1875e122ae2a3189de53b
TIMEZONE = UTC
```

3. Click "Save"

✅ **Variables are secure in Railway (not visible publicly)**

---

## Step 4: Set Start Command (1 minute)

In Railway dashboard:

1. Go to **Settings** tab
2. Find "Start Command" field
3. Set it to: `python main.py`
4. Save

✅ **Railway will run your bot with this command**

---

## Step 5: Deploy (1 minute)

1. Click "Deploy" button
2. Watch the logs appear
3. Look for: `"Starting Contest Tracker Bot..."`
4. When logs show: `"Reminder scheduler started"` → Bot is running! ✅

---

## Step 6: Test on Telegram (1 minute)

Open Telegram and find your bot (search by name or bot link)

Send these commands one by one:

```
/start
```
**Expected:** Welcome message with commands list

```
/subscribe Codeforces
```
**Expected:** ✅ Subscribed to Codeforces!

```
/upcoming
```
**Expected:** List of upcoming Codeforces contests (may take 3-5 seconds)

```
/weekly
```
**Expected:** Statistics showing contests this week

```
/help
```
**Expected:** All commands listed

✅ **If all respond correctly, your bot is LIVE!**

---

## 📊 Troubleshooting During Deployment

### Issue: Deployment fails
**Solution:** 
1. Check Railway logs for error message
2. Common: Missing environment variables
3. Verify all 3 env vars are added

### Issue: Bot doesn't respond
**Solution:**
1. Wait 30 seconds for bot to fully start
2. Check Railway logs: `"Reminder scheduler started"`
3. Verify TELEGRAM_BOT_TOKEN is correct

### Issue: /upcoming shows no contests
**Solution:**
1. Verify CLIST credentials are correct
2. Wait for API response (3-5 seconds)
3. Check you're subscribed to a platform first

### Issue: Reminders not working
**Solution:**
1. Wait 60+ seconds (scheduler checks every minute)
2. Verify bot is running (check logs)
3. Check "Reminder scheduler started" message

---

## ✅ Deployment Checklist

Before you start:
- [x] Code is committed and pushed ✅
- [x] .env has your credentials ✅
- [x] Requirements.txt is complete ✅

During deployment:
- [ ] Create Railway account
- [ ] Connect GitHub repo
- [ ] Add environment variables
- [ ] Set start command: `python main.py`
- [ ] Click Deploy
- [ ] Wait for "Reminder scheduler started"

After deployment:
- [ ] /start works
- [ ] /upcoming shows contests
- [ ] /subscribe works
- [ ] /weekly shows stats
- [ ] /help displays commands
- [ ] Bot is live! 🎉

---

## 🎯 Quick Railway Deployment Video

**If you prefer video instructions:**
1. Go to railway.app/docs
2. Search "GitHub deployment"
3. Follow the video guide

**It's essentially:**
1. Connect GitHub
2. Select repo
3. Add variables
4. Deploy!

---

## 📞 Railway Support During Deployment

If you get stuck:
1. Railway Discord: discord.gg/railway
2. Docs: railway.app/docs
3. Status: status.railway.app

---

## 🎉 Expected Result

After ~2-3 minutes of deployment:

✅ Bot is running 24/7
✅ Responds to /start instantly
✅ Fetches contests from CLIST API
✅ Sends reminders every 60 seconds
✅ Persists data in database
✅ Always-on (no sleeping)

---

## 🔗 Your Bot Link

After deployment, Railway gives you a unique URL.

You can share your bot like:
```
https://t.me/your_bot_name
```

Find the exact link in Railway dashboard under "Railway URL"

---

## 💡 Pro Tips

**Tip 1: Auto-Redeploy on Push**
When you push to GitHub, Railway auto-redeploys! (No manual push needed)

**Tip 2: Monitor Logs**
In Railway dashboard, always watch the logs to see:
- Bot startup messages
- API calls to CLIST
- User commands
- Errors (if any)

**Tip 3: Keep This Handy**
Railway dashboard shows:
- Real-time logs
- Deployment history
- Environment variables
- Restart button (if needed)

---

## ⏱️ Time Breakdown

| Step | Time | Status |
|------|------|--------|
| Prepare repo | 2 min | ✅ DONE |
| Create Railway account | 3 min | NEXT |
| Add variables | 2 min | AFTER |
| Set command | 1 min | AFTER |
| Deploy | 1 min | AFTER |
| Test on Telegram | 1 min | AFTER |
| **TOTAL** | **10 min** | 🚀 |

---

## 🎊 After Deployment

Once bot is live:

1. **Test all commands** (see Step 6 above)
2. **Send /upcoming** - Verify contest fetching works
3. **Wait 60 seconds** - Test reminder system
4. **Check logs** - Verify no errors
5. **Celebrate!** 🎉 Your bot is live!

---

## Next: Real-Time Monitoring

In Railway:
- Logs stream in real-time
- You can see exactly what bot is doing
- Errors are highlighted in red
- Performance metrics show CPU/RAM

---

## 🚀 YOU'RE READY!

Everything is prepared. All you need to do is:

1. Go to railway.app
2. Connect your GitHub repo
3. Add the 3 environment variables
4. Click Deploy
5. Test commands on Telegram

**That's it!** 🎯

---

**Status:** ✅ Ready for Railway deployment
**Time to completion:** ~10 minutes
**Cost:** $5/month (first month may be free trial)

Let's go live! 🚀
