# Morning Fetch - Indian Land/Lancaster News Automation

Automated news aggregation and content generation for Indian Land and Lancaster County, SC.

## How It Works
1. Fetches RSS feeds from 10 local news sources
2. Filters for Indian Land/Lancaster relevance
3. Grades stories 0-100 based on real estate impact
4. Generates Instagram Reels scripts, captions, and blog posts via Claude AI
5. Sends to Make.com for distribution

## Setup
1. Add GitHub Secrets:
   - `ANTHROPIC_API_KEY` - Your Claude API key
   - `MAKE_WEBHOOK_URL` - Your Make.com webhook URL

2. Runs automatically at 4:00 AM EST daily

3. To test manually: Go to Actions → Morning Fetch → Run workflow

## Local Testing
