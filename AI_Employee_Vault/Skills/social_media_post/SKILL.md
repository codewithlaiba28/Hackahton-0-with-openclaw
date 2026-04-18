---
name: social_media_post
description: Draft and schedule posts for Facebook, Instagram, and Twitter/X, requiring human approval before posting.
---

# Skill: Social Media Post

## Purpose
Draft and schedule posts for Facebook, Instagram, and Twitter/X.
Always require human approval before posting anywhere.

## Trigger
- Manual: user drops topic into /Inbox/social_topic.md
- Scheduled: part of weekly content plan

## Steps
1. Read topic or source content
2. Draft platform-specific versions:
 - Facebook: 100-200 words, conversational, 1-2 hashtags
 - Instagram: 50-100 words, visual-focused, 5-10 hashtags
 - Twitter/X: under 280 characters, punchy, 1-2 hashtags
3. Save all drafts to /Pending_Approval/SOCIAL_<platform>_<date>.md
4. Wait for human approval
5. On approval, call appropriate poster script
6. Collect engagement summary after 24 hours
7. Log everything to /Logs/YYYY-MM-DD.json

## Rules
- No political or controversial content
- No client names without permission
- Always professional and on-brand
- Never post same content twice
