# reddit-summarizer

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
