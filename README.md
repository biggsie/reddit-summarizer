# reddit-summarizer
Courtesy of Thomas Williams
https://www.linkedin.com/posts/thomas-williams-design_tldr-i-built-an-app-with-anthropic-claude-activity-7424195184655114240-ACGa?utm_source=share&utm_medium=member_desktop&rcm=ACoAAABL1oMBgSNlK1s48kGobohUFTx30VW4ai4

TL/DR: I built an app with Anthropic Claude Code that reads subreddits and emails me a daily digest. 

Last week I tried Claude Code for the first time, with the goal to just learn more about it. But, a week later, I’ve built and deployed my first app! 

After disconnecting from social over the holiday break, I found I was missing a few subreddits I follow, but not the time I was sinking into them. This made for the perfect use case: an app that could read reddit for me. Here’s what it does: 

→ Scans my favorite subreddits
→ Ranks posts by quality (custom algorithm)
→ Sends daily digest with AI summaries of posts and comments
→ Responsive design, light/dark mode
→ Dashboard to manage everything

The app sends the digest at 6:00am every morning with 10–12 posts. All up (not including my Claude subscription) it costs ~$0.37/month to run. It took me around 8 hours total and I didn't use any design tools.

Stack:
Python/FastAPI (backend + dashboard)
Anthropic Claude Haiku (AI summaries)
Reddit API (content fetching)
Resend (email delivery)
Railway (deployment + scheduling)
GitHub

Algorithm:
Velocity (upvotes per hour to catch trending content early) 
Engagement quality (comment-to-upvote ratio)
Community approval (upvote ratio)
Popularity (percentile ranking within subreddit)
Content signals (title quality, post type)
Round-robin selection  (balanced representation across subreddits)

Dashboard: 
Add/remove subreddits 
Thresholds and post preferences (including no. of posts) 
Generate previews and test emails 
Responsive with native light/dark mode 

Costs: 
Claude Haiku: ~$0.012 per digest
Monthly: ~$0.37 for daily AI summaries
Everything else on free tier 

See demo vidoe for design and UI guidelines: https://drive.google.com/file/d/1x7T3QzdkY4tAggwvNv_Wv0MRTy6OmKI_/view?usp=sharing

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- API keys: Anthropic (AI), Resend (email)
- **No Reddit API key needed!**

### Run Locally

```bash
# 1. Clone and setup
git clone <repo-url>
cd reddit-summarizer
cp .env.example .env
# Edit .env with your API keys

# 2. Start with Docker
docker-compose up --build

# Or use Makefile
make up

# 3. Open dashboard
open http://localhost:8000
```

### Deploy to Railway

1. Connect your GitHub repository to Railway
2. Add environment variables (see `.env.example`)
3. Add persistent volume: `/data` mount path
4. Deploy automatically!

**Full setup guide:** See [SETUP.md](SETUP.md)

---

## Technical Implementation

### Architecture
- **Backend**: FastAPI with SQLAlchemy (SQLite/PostgreSQL)
- **Reddit**: Public JSON API (no authentication needed)
- **Dependency Management**: uv (10-100x faster than pip)
- **Containerization**: Docker with multi-stage builds
- **Scheduler**: APScheduler for automated digests
- **AI**: Claude Haiku 4.5 for cost-effective summaries
- **Email**: Resend with responsive HTML templates

### Project Structure
```
reddit-summarizer/
├── app/
│   ├── main.py              # FastAPI application
│   ├── reddit/              # Reddit API integration
│   ├── ai/                  # Claude summarization
│   ├── email/               # Email delivery
│   └── api/                 # REST API & scheduler
├── templates/               # HTML dashboard
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Local development
└── pyproject.toml          # Dependencies (uv)
```

### Key Features

**Ranking Algorithm:**
- Velocity scoring (upvotes/hour)
- Engagement quality (comments/upvotes ratio)
- Community approval (upvote ratio)
- Percentile ranking within subreddit
- Title quality assessment
- Content type scoring
- Round-robin selection for diversity

**Dashboard:**
- Add/remove subreddits
- Configure preferences
- Generate preview digests
- Send test emails
- Responsive design with native light/dark mode

**Email Digest:**
- Beautiful HTML templates
- AI-generated summaries
- Post metadata (score, comments)
- Direct links to discussions
- Mobile-friendly design

### Development

```bash
# Start development server with hot reload
docker-compose up

# View logs
make logs

# Access container shell
make shell

# Run tests
make test

# Clean up
make clean
```

### Commands Reference

Using Makefile for convenience:
- `make build` - Build Docker image
- `make up` - Start services in background
- `make down` - Stop services
- `make logs` - View live logs
- `make restart` - Restart services
- `make shell` - Access container shell
- `make clean` - Remove containers and volumes

### Environment Variables

**Required (only 3!):**
- `ANTHROPIC_API_KEY` - Claude API key for summaries
- `RESEND_API_KEY` - Email API key for delivery
- `USER_EMAIL` - Recipient email address

**Optional:**
- `DIGEST_TIME` - Send time (default: 06:00)
- `POSTS_PER_DIGEST` - Number of posts (default: 12)
- `DATABASE_URL` - Database connection string

**No Reddit credentials needed!** Uses public JSON API.

### Deployment Notes

**Railway:**
- Automatically detects Dockerfile
- Use persistent volumes for SQLite (`/data` mount)
- Environment variables via Railway dashboard
- Auto-deploys on git push

**Alternative Platforms:**
- Docker container works on any platform
- AWS ECS, Google Cloud Run, Azure Container Apps
- Self-hosted with docker-compose

### Cost Optimization

- Claude Haiku (not Opus/Sonnet) for summaries
- Efficient prompts (2-3 sentence summaries)
- Batch processing where possible
- Free tiers for email and hosting
- ~$0.37/month total operating cost

### Monitoring

Check logs for:
- "Scheduler started" - Scheduler initialized
- "Digest sent successfully" - Daily digest sent
- API errors or rate limits

### Troubleshooting

Common issues:
1. **Email not sending**: Verify Resend domain and API key
2. **No posts found**: Check subreddit names (no "r/" prefix) and thresholds
3. **Rate limiting**: Reddit's public API limits ~60 req/min (sufficient for daily digest)
4. **Scheduler not running**: Verify DIGEST_TIME format (HH:MM)
5. **Database errors**: Ensure volume is mounted correctly

See [SETUP.md](SETUP.md) for detailed troubleshooting.

---

## Contributing

This is a personal project but feel free to:
- Fork and customize for your needs
- Report issues or bugs
- Suggest improvements
- Share your modifications

## License

MIT License - feel free to use and modify.
