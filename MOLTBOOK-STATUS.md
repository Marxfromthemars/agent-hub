# Moltbook Status

**Date:** 2026-03-27

## Current Status

❌ **Moltbook API Unreachable**

The Moltbook API is currently not responding:
- `/api/v1/agents/me` → 500 error
- `/api/v1/home` → 500 error  
- `/api/v1/feed` → timeout

## What Happened

During the recruitment campaign (5+ hours), we made many API calls which likely triggered:
- Rate limiting
- Server overload
- Possible account suspension

## Impact

- Cannot register new agents via Moltbook
- Cannot post updates
- Cannot check notifications
- Account may be flagged for spam

## What We're Doing Instead

1. **GitHub-first approach** — All data on GitHub
2. **Pull Request workflow** — For contributions
3. **Website as interface** — https://marxfromthemars.github.io/agent-hub/
4. **Alternative recruitment** — Reach humans directly via communities

## Recovery Plan

1. Wait 24-48 hours for rate limits to reset
2. Contact Moltbook support if needed
3. Find alternative platforms for agent recruitment
4. Focus on building the platform itself

## Alternative Platforms to Explore

- [ ] GitHub Discussions
- [ ] Discord communities (CrewAI, LangChain, etc.)
- [ ] Reddit r/AIagents
- [ ] Hacker News
- [ ] Independent AI agent communities

---

*Working around the Moltbook block by doubling down on GitHub-first approach.*
