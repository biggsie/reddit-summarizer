# Reddit Summarizer - Setup Guide

Complete guide to set up and deploy your Reddit Summarizer app.

## Prerequisites

1. **Python 3.11+** installed locally
2. **Reddit API** credentials
3. **Anthropic API** key
4. **Resend API** key (or verified domain)
5. **Railway account** (for deployment)

## Step 1: Reddit API Setup

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - **Name**: Reddit Summarizer
   - **Type**: Select "script"
   - **Description**: Daily Reddit digest
   - **About URL**: (leave blank)
   - **Redirect URI**: http://localhost:8000
4. Click "Create App"
5. Save your:
   - **Client ID** (under app name)
   - **Client Secret**

## Step 2: Anthropic API Key

1. Go to https://console.anthropic.com/
2. Navigate to API Keys section
3. Create a new API key
4. Save the key securely

## Step 3: Resend API Setup

1. Go to https://resend.com/
2. Sign up for a free account
3. Add and verify your domain (or use their test domain)
4. Generate an API key
5. Update `app/email/sender.py`:
   ```python
   self.from_email = "digest@yourdomain.com"  # Change to your verified domain
   ```

## Step 4: Local Setup

1. **Clone and navigate to project**:
   ```bash
   cd reddit-summarizer
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

5. **Edit `.env` with your credentials**:
   ```env
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   REDDIT_USER_AGENT=RedditSummarizer/1.0

   ANTHROPIC_API_KEY=your_anthropic_api_key

   RESEND_API_KEY=your_resend_api_key

   USER_EMAIL=your_email@example.com

   DATABASE_URL=sqlite:///./reddit_summarizer.db

   DIGEST_TIME=06:00
   POSTS_PER_DIGEST=12
   ```

## Step 5: Run Locally

1. **Start the application**:
   ```bash
   python -m app.main
   ```

   Or with auto-reload:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Open dashboard**:
   - Navigate to: http://localhost:8000
   - You should see the dashboard interface

3. **Configure your digest**:
   - Add subreddits (e.g., "programming", "python", "technology")
   - Update your email and preferences
   - Click "Send Test Email" to verify email works
   - Click "Generate & Send Preview" to see a sample digest

## Step 6: Deploy to Railway

1. **Install Railway CLI** (optional):
   ```bash
   npm install -g @railway/cli
   ```

2. **Create Railway project**:
   - Go to https://railway.app/
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account and select the repository

3. **Set environment variables**:
   - In Railway dashboard, go to your project
   - Click on "Variables" tab
   - Add all variables from your `.env` file:
     - `REDDIT_CLIENT_ID`
     - `REDDIT_CLIENT_SECRET`
     - `REDDIT_USER_AGENT`
     - `ANTHROPIC_API_KEY`
     - `RESEND_API_KEY`
     - `USER_EMAIL`
     - `DIGEST_TIME`
     - `POSTS_PER_DIGEST`
     - `DATABASE_URL` (use: `sqlite:///./reddit_summarizer.db`)

4. **Deploy**:
   - Railway will automatically detect the `Procfile`
   - Your app will deploy automatically
   - You'll get a public URL (e.g., `your-app.up.railway.app`)

5. **Update Resend domain** (if using custom domain):
   - Update the sender email in Railway environment variables

## Step 7: Verify Deployment

1. Visit your Railway URL
2. Test the dashboard
3. Send a test email
4. Generate a preview digest

## Monitoring & Maintenance

### Check Logs

**Railway**:
- Go to your project → Deployments → View logs
- Look for "Digest sent successfully" messages

### Update Scheduler

The app automatically sends digests at your configured time. To change:
1. Update `DIGEST_TIME` environment variable in Railway
2. Restart the deployment

### Database Backup

SQLite database is stored in the container. For production:
- Consider using Railway's PostgreSQL addon
- Update `DATABASE_URL` to use PostgreSQL
- Modify `requirements.txt` to include `psycopg2-binary`

### Cost Optimization

- **Claude Haiku**: ~$0.012 per digest
- **Resend**: Free tier (3,000 emails/month)
- **Railway**: Free tier ($5 credit/month)
- **Total**: ~$0.37/month for daily digests

## Troubleshooting

### Email Not Sending

1. Check Resend API key is correct
2. Verify domain is validated in Resend dashboard
3. Check Railway logs for errors
4. Try sending a test email from dashboard

### No Posts Found

1. Verify subreddit names are correct (no "r/" prefix needed)
2. Check min_upvotes and min_comments thresholds
3. Enable more subreddits
4. Check Reddit API credentials

### Scheduler Not Running

1. Verify Railway deployment is not sleeping (use web endpoint)
2. Check `DIGEST_TIME` format (HH:MM)
3. Review Railway logs for scheduler errors
4. Consider Railway's cron jobs for guaranteed execution

### Database Issues

1. Check `DATABASE_URL` is set correctly
2. Verify write permissions
3. Consider switching to PostgreSQL for production

## Advanced Configuration

### Using PostgreSQL on Railway

1. Add PostgreSQL plugin in Railway
2. Update `requirements.txt`:
   ```
   psycopg2-binary==2.9.9
   ```
3. Update `DATABASE_URL` to use the PostgreSQL connection string
4. Redeploy

### Custom Email Templates

Edit `app/email/templates.py` to customize:
- Email styling
- Layout
- Colors
- Footer content

### Adjusting Ranking Algorithm

Modify weights in `app/reddit/ranking.py`:
```python
weights = {
    'velocity': 0.25,      # Trending content
    'engagement': 0.20,    # Discussion quality
    'approval': 0.20,      # Community approval
    'percentile': 0.15,    # Popularity ranking
    'title': 0.10,         # Title quality
    'content': 0.10        # Content type
}
```

## Support

For issues:
1. Check Railway logs
2. Test locally first
3. Verify all API keys are valid
4. Review error messages in browser console

## Next Steps

- Add more subreddits
- Adjust post count and timing
- Customize email template styling
- Monitor costs and optimize
- Consider adding webhook notifications
