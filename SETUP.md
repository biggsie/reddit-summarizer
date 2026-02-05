# Reddit Summarizer - Setup Guide

Complete guide to set up and deploy your Reddit Summarizer app with **Docker** and **uv**.

## Prerequisites

1. **Docker & Docker Compose** installed locally
2. **uv** - Fast Python package installer ([Install](https://github.com/astral-sh/uv))
3. **Anthropic API** key (for AI summaries)
4. **Resend API** key (for email delivery)
5. **Railway account** (for deployment - optional)

**No Reddit API credentials needed!** Uses public JSON endpoints.

## Quick Start with Docker (Recommended)

```bash
# 1. Clone and navigate
cd reddit-summarizer

# 2. Set up environment
cp .env.example .env
# Edit .env with your credentials

# 3. Build and run with Docker Compose
docker-compose up --build

# 4. Open dashboard
open http://localhost:8000
```

That's it! The app is running with persistent storage.

## Step 1: Anthropic API Key

1. Go to https://console.anthropic.com/
2. Navigate to API Keys section
3. Create a new API key
4. Save the key securely

## Step 2: Resend API Setup

1. Go to https://resend.com/
2. Sign up for a free account
3. Add and verify your domain (or use their test domain)
4. Generate an API key
5. Update `app/email/sender.py`:
   ```python
   self.from_email = "digest@yourdomain.com"  # Change to your verified domain
   ```

## Step 3: Local Setup

### Option A: Docker (Recommended)

1. **Install Docker**:
   - Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Linux: `sudo apt-get install docker.io docker-compose`
   - Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop)

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` with your credentials**:
   ```env
   # Only 3 required values!
   ANTHROPIC_API_KEY=your_anthropic_api_key
   RESEND_API_KEY=your_resend_api_key
   USER_EMAIL=your_email@example.com

   # Optional configuration
   DATABASE_URL=sqlite:////data/reddit_summarizer.db
   DIGEST_TIME=06:00
   POSTS_PER_DIGEST=12
   ```

4. **Build and run**:
   ```bash
   # Build and start
   docker-compose up --build

   # Or run in background
   docker-compose up -d

   # View logs
   docker-compose logs -f

   # Stop
   docker-compose down
   ```

5. **Open dashboard**: http://localhost:8000

### Option B: Local Python with uv

1. **Install uv**:
   ```bash
   # Mac/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Or with pip
   pip install uv
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -r pyproject.toml
   ```

3. **Create `.env` file** (same as above)

4. **Run**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Step 4: Configure Your Digest

1. **Open dashboard**: http://localhost:8000

2. **Add subreddits**:
   - Click on subreddit input
   - Enter name (e.g., "programming", "python", "technology")
   - Click "Add"
   - Start with 3-5 subreddits

3. **Update preferences**:
   - Set your email address
   - Choose digest time (24-hour format)
   - Set posts per digest (5-20 recommended)
   - Click "Save Preferences"

4. **Test**:
   - Click "📧 Send Test Email" - verify email works
   - Click "👀 Generate & Send Preview" - see sample digest
   - Preview won't mark posts as sent

## Step 5: Deploy to Railway

### Railway Setup

1. **Create Railway account**: https://railway.app/

2. **Create new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub and select the repository

3. **Railway automatically detects Docker**:
   - Sees `Dockerfile` and `railway.toml`
   - Builds container automatically
   - No additional configuration needed

### Configure Environment Variables

In Railway dashboard, add these variables:

```
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key
RESEND_API_KEY=your_resend_api_key
USER_EMAIL=your_email@example.com

# Optional
DIGEST_TIME=06:00
POSTS_PER_DIGEST=12
DATABASE_URL=sqlite:////data/reddit_summarizer.db
```

**Note:** No Reddit API credentials needed! The app uses Reddit's public JSON API.

### Add Persistent Volume (IMPORTANT!)

Railway provides persistent volumes for Docker containers:

1. Go to your Railway project
2. Click on your service
3. Go to "Volumes" tab
4. Click "Add Volume"
5. Configure:
   - **Mount Path**: `/data`
   - **Name**: `reddit-data` (or any name)
6. Save

This ensures your SQLite database persists across deployments.

### Deploy

1. Railway auto-deploys on git push
2. Or manually trigger from Railway dashboard
3. You'll get a public URL (e.g., `your-app.up.railway.app`)

### Update Resend Email Address

If using custom domain, update `app/email/sender.py` before deploying:
```python
self.from_email = "digest@yourdomain.com"
```

## Docker Commands Reference

```bash
# Build image
docker build -t reddit-summarizer .

# Run container
docker run -p 8000:8000 --env-file .env reddit-summarizer

# Run with volume
docker run -p 8000:8000 --env-file .env -v reddit-data:/data reddit-summarizer

# Using Docker Compose (recommended)
docker-compose up --build        # Build and start
docker-compose up -d             # Start in background
docker-compose down              # Stop
docker-compose logs -f           # View logs
docker-compose restart           # Restart services

# Access container shell
docker-compose exec app sh

# View database
docker-compose exec app ls -la /data
```

## Monitoring & Maintenance

### Check Logs

**Docker Compose (local)**:
```bash
docker-compose logs -f
```

**Railway**:
- Go to project → Deployments → View logs
- Look for "Digest sent successfully" messages

### Database Access

**Local (Docker)**:
```bash
# Access container
docker-compose exec app sh

# View database file
ls -la /data/reddit_summarizer.db

# Or mount and use sqlite3
docker-compose exec app sqlite3 /data/reddit_summarizer.db
```

### Update Scheduler Time

1. Update `DIGEST_TIME` environment variable
2. Restart:
   - **Local**: `docker-compose restart`
   - **Railway**: Redeploy or restart service

### Backup Database

**Local**:
```bash
docker cp $(docker-compose ps -q app):/data/reddit_summarizer.db ./backup.db
```

**Railway**:
- Railway volumes persist automatically
- Consider periodic backups via Railway CLI
- For production, consider migrating to PostgreSQL

## Migrating to PostgreSQL (Optional)

For better production reliability:

1. **Add to Railway**:
   - Click "New" → "Database" → "PostgreSQL"
   - Railway provides connection string

2. **Update dependencies** in `pyproject.toml`:
   ```toml
   dependencies = [
       # ... existing deps ...
       "psycopg2-binary==2.9.9",
   ]
   ```

3. **Update `DATABASE_URL`** in Railway:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/db
   ```

4. **Rebuild and deploy**:
   ```bash
   git add pyproject.toml
   git commit -m "Add PostgreSQL support"
   git push
   ```

## Cost Breakdown

### Development
- **Docker**: Free (local)
- **uv**: Free
- **API Testing**: ~$0.15-0.25

### Monthly Operation
- **Claude Haiku**: ~$0.012/digest × 30 = $0.36
- **Resend**: Free (3,000 emails/month)
- **Railway**:
  - Free tier: $5 credit/month (sufficient)
  - OR $5/month for hobby plan (500 hours)
- **Total**: ~$0.36-$5.36/month

## Troubleshooting

### Docker Issues

**Build fails**:
```bash
# Clear cache and rebuild
docker-compose build --no-cache
```

**Port already in use**:
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

**Volume permissions**:
```bash
# Check volume
docker volume inspect reddit-summarizer_reddit-data

# Remove and recreate
docker-compose down -v
docker-compose up --build
```

### Email Not Sending

1. Verify Resend API key
2. Check domain is verified
3. View logs: `docker-compose logs -f`
4. Test email from dashboard

### No Posts Found

1. Check subreddit names (no "r/" prefix)
2. Verify min thresholds aren't too high
3. Enable more subreddits
4. Check Reddit API credentials in logs

### Scheduler Not Running

1. Check logs for scheduler startup: "Scheduler started"
2. Verify `DIGEST_TIME` format (HH:MM)
3. Check timezone (container uses UTC by default)
4. Consider Railway cron for guaranteed execution

## Development Workflow

### Local Development with Hot Reload

```bash
# Edit code
# Docker Compose auto-reloads on changes (volumes mounted)
docker-compose logs -f  # Watch logs

# Or run without Docker for faster iteration
uv pip install -r pyproject.toml
uvicorn app.main:app --reload
```

### Testing Changes

```bash
# Rebuild after dependency changes
docker-compose up --build

# Test specific component
docker-compose exec app python -c "from app.reddit.client import RedditClient; print('OK')"
```

### Deploying Updates

```bash
git add .
git commit -m "Your changes"
git push origin main

# Railway auto-deploys on push
```

## Advanced Configuration

### Custom Email Templates

Edit `app/email/templates.py` to customize:
- HTML structure
- Styling and colors
- Layout and spacing
- Footer content

### Ranking Algorithm Tuning

Modify weights in `app/reddit/ranking.py`:
```python
weights = {
    'velocity': 0.25,      # Trending content
    'engagement': 0.20,    # Discussion quality
    'approval': 0.20,      # Community approval
    'percentile': 0.15,    # Popularity
    'title': 0.10,         # Title quality
    'content': 0.10        # Content type
}
```

### Using Railway Cron (Alternative to APScheduler)

For guaranteed execution, use Railway's cron jobs:

1. Create separate cron service in Railway
2. Configure schedule
3. Call your `/api/send-digest` endpoint

## Security Best Practices

1. **Never commit `.env`** - already in `.gitignore`
2. **Use Railway secrets** for production
3. **Rotate API keys** periodically
4. **Enable HTTPS** (Railway provides automatically)
5. **Review logs** for suspicious activity

## Support & Resources

- **Railway Docs**: https://docs.railway.app/
- **uv Docs**: https://github.com/astral-sh/uv
- **Docker Docs**: https://docs.docker.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

## Next Steps

✅ Deploy to Railway
✅ Add your favorite subreddits
✅ Send test digest
✅ Enjoy your daily summaries!

Consider:
- Adding webhook notifications
- Creating weekly recap digest
- Building mobile app interface
- Implementing user authentication for multi-user support
