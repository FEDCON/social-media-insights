# Social-Media-Insights Skill — Quick Start

## What Is This?

A skill that analyzes social media posts (TikTok, Instagram, Twitter) and tells you:
- What the post is about (sentiment: positive/negative/neutral)
- What topics it covers
- How relevant it is to your work
- What you should do about it (specific recommendations)

## I'm A New Agent — What Do I Do?

### 1. Give It Posts to Analyze

Create a file called `input.json`:

```json
{
  "posts": [
    "https://www.tiktok.com/@someuser/video/123",
    "https://www.instagram.com/p/ABC123/",
    "https://twitter.com/someuser/status/456"
  ]
}
```

### 2. Run The Skill

```bash
bash ./social-media-insights/pipeline.sh --input-file input.json
```

### 3. Read The Results

Look for `output/2026-04-29-full-analysis.json` (or today's date).

The file contains:
- **extracted_posts**: What the skill found in each post (text, author, likes, etc.)
- **analysis**: Sentiment, topics, themes for each post
- **recommendations**: Specific things you should do with this info

### 4. Act On Recommendations

Each recommendation has:
- **priority_score**: How important (0 = ignore, 1 = urgent)
- **actions**: What to do (investigate_topic, monitor_trend, etc.)
- **implementation_steps**: Exact steps to follow
- **time_estimate_hours**: How long it'll take

Pick the highest priority_score and do those steps.

## Real-World Example

**Input**: TikTok video about AI automation

**Output**: 
```json
{
  "sentiment": {"score": 0.8, "label": "positive"},
  "topics": [
    {"topic": "AI/automation", "relevance": 0.9}
  ],
  "recommendations": [{
    "priority_score": 0.85,
    "actions": [{
      "action": "investigate_topic",
      "topic": "AI/automation",
      "implementation_steps": [
        "1. Review current workflows",
        "2. Compare against video insights",
        "3. Test improvement in sandbox",
        "4. Measure impact"
      ]
    }]
  }]
}
```

**You do**: Follow the 4 steps. Report results.

## Troubleshooting

### "Apify call failed"
- The post URL might be deleted or private
- Try a different URL
- Check your internet connection

### "No output file created"
- Did you run the right command? (check the command above)
- Is your input.json valid JSON? (no trailing commas, quotes correct)
- Are the URLs real social media links?

### "Low priority_score on recommendations"
- The post might not be relevant to your work
- That's OK — skip it and try different posts

## Need Help?

Recommendations not clear? Check the SKILL.md file for detailed documentation.
