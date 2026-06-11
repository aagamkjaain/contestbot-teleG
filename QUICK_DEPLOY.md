# Quick Start: Deploy to Railway 🚀

## Prerequisites ✅
- GitHub account
- Railway account (railway.app)
- Your bot repo on GitHub

## 5-Minute Deployment

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Click "Start new project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub

### Step 2: Select Your Repository
1. Search for "telebot" or your repo name
2. Select the repository
3. Click "Deploy now"

Railway will auto-detect Python and install requirements.txt ✅

### Step 3: Add Environment Variables
In Railway dashboard, go to **Variables** tab:

```
TELEGRAM_BOT_TOKEN = 8816657732:AAHS9Zj3zeoQKlpwfMoo35vcx1eiSszvz80
CLIST_USERNAME = aagamkjain
CLIST_API_KEY = 11ccd225284ae7d0bba1875e122ae2a3189de53b
TIMEZONE = UTC
```

### Step 4: Set Startup Command
In Railway dashboard, go to **Settings** tab:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python main.py
```

### Step 5: Deploy
1. Click "Deploy" button
2. Watch the logs - should see "Starting Contest Tracker Bot..."
3. Once you see "Reminder scheduler started", bot is running! ✅

### Step 6: Test Your Bot
Open Telegram and find your bot:

```
/start
/upcoming
/subscribe Codeforces
/weekly
```

---

## Troubleshooting

### Bot not responding
**Check:**
1. Bot token is correct (copy from .env)
2. Click "View logs" in Railway to see errors
3. Verify Telegram bot exists (@BotFather)

### Contests not showing
**Check:**
1. CLIST_USERNAME and CLIST_API_KEY are correct
2. CLIST account is active (clist.by)
3. Look for API errors in logs

### Reminders not sending
**Wait:** Scheduler checks every 60 seconds
**Check:** Look for "Reminder sent" in logs

---

## After Deployment

### Monitoring
- Railway dashboard shows real-time logs
- Monitor memory/CPU usage
- Set up alerts (optional)

### Updates
When you push new code to GitHub:
1. Railway auto-detects changes
2. Automatically redeploys
3. Old bot stops, new bot starts
4. No downtime! ✅

### Rolling Back
If something breaks:
1. Go to "Deployments" tab in Railway
2. Select previous deployment
3. Click "Redeploy"
4. Done! 🔄

---

## Cost Breakdown

**Railway Pricing:**
- First $5 free per month
- Then $0.50/hour of compute
- For a bot: ~$5/month total
- Includes: 1 GB RAM, unlimited bandwidth

**Alternatives:**
- **Render:** Free (but sleeps after 15 min)
- **Fly.io:** Free tier available
- **AWS/GCP:** Pay-as-you-go (more complex)

---

## Next Steps

1. **Commit and push** (you already did ✅)
2. **Go to railway.app**
3. **Deploy from GitHub** (5 minutes)
4. **Test bot** (2 minutes)
5. **Celebrate!** 🎉

---

## Support

**Railway Issues?**
- Check [Railway Docs](https://docs.railway.app)
- Discord support (railway.app/support)

**Bot Issues?**
- Check logs in Railway dashboard
- Review TESTING.md for debugging

**API Issues?**
- Check CLIST status: clist.by
- Telegram Bot status: @BotFather

---

## Deployment Checklist

- [ ] All code pushed to GitHub
- [ ] .env NOT in repo (in .gitignore)
- [ ] Railway account created
- [ ] Repository connected to Railway
- [ ] Environment variables added
- [ ] Start command set to `python main.py`
- [ ] Deployment started
- [ ] Logs show "Reminder scheduler started"
- [ ] Bot responds to /start
- [ ] Bot shows contests with /upcoming
- [ ] Reminders scheduled (wait 60 seconds)
- [ ] Celebrate deployment! 🎉

