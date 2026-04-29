# Social-Media-Insights Skill — Full 17-Step Pipeline

Complete social media post analysis + context-aware agent recommendations.

## What It Does

Processes social media post URLs (TikTok, Instagram, Twitter/X) through a complete 17-step pipeline:

1. **Input Validation** (3 steps): Parse URLs, identify platform
2. **Extraction** (1 step): Get post content, author, engagement metrics
3. **Analysis** (5 steps): Sentiment, topics, themes, insights, trend signals
4. **Context Matching** (3 steps): Score relevance to agent's projects/goals/expertise
5. **Recommendations** (3 steps): Generate specific, actionable improvements agent can implement
6. **Output** (2 steps): Structured JSON ready for agent consumption

## Usage

```bash
bash ./social-media-insights/pipeline.sh --input-file posts.json
```

## Input Format

`posts.json`:
```json
{
  "test_name": "social-media-insights-test",
  "posts": [
    "https://www.tiktok.com/@user/video/123",
    "https://www.instagram.com/p/ABC123/",
    "https://twitter.com/user/status/456"
  ]
}
```

## Output Structure

```json
{
  "test_id": 1777490299,
  "timestamp": "2026-04-29T15:18:19Z",
  "stages_completed": 6,
  "steps_completed": 17,
  "posts_processed": 3,
  "extracted_posts": [
    {
      "url": "...",
      "platform": "tiktok|instagram|twitter",
      "content": {
        "text": "...",
        "author": {"handle": "..."},
        "engagement": {"likes": 0, "comments": 0, "shares": 0, "views": 0}
      }
    }
  ],
  "analysis": [
    {
      "sentiment": {
        "score": 0.68,
        "label": "positive",
        "confidence": 0.74
      },
      "topics": [
        {"topic": "AI/automation", "relevance": 0.85},
        {"topic": "workflow optimization", "relevance": 0.72}
      ],
      "themes": ["efficiency", "technology trends"],
      "insights": ["Relevant to agent self-improvement"]
    }
  ],
  "recommendations": [
    {
      "id": "rec_001",
      "priority_score": 0.72,
      "actions": [
        {
          "action": "investigate_topic",
          "topic": "AI/automation",
          "urgency": "medium",
          "implementation_steps": [...]
        }
      ]
    }
  ]
}
```

## Agent Integration

After receiving recommendations:

1. **Review** recommendations by priority_score
2. **Select** highest-priority action to implement
3. **Execute** implementation_steps in agent workflow
4. **Measure** impact on project metrics
5. **Report** results back

## Requirements

- Python 3
- Bash
- Internet access (for Apify when full extraction enabled)
- Optional: APIFY_API_KEY (for full post content extraction)

## Pipeline Stages

### Stage 1: Input Validation (Steps 1-3)
- Parse social media URLs
- Identify platform (TikTok, Instagram, Twitter/X)
- Validate URL format

### Stage 2: Extraction (Step 4)
- Scrape post content using Apify actors
- Extract author/engagement metadata
- Return structured post data

**Status**: ✓ Real Apify integration active
- TikTok: Free TikTok Scraper actor
- Instagram: Fast Instagram Post Scraper actor
- Twitter/X: Twitter Scraper actor

### Stage 3: Analysis (Steps 5-9)
- **Sentiment** (score 0-1, positive/neutral/negative)
- **Topics** (extracted keywords with relevance scores)
- **Themes** (grouped insights)
- **Key Insights** (what makes this post relevant)
- **Trend Signals** (emerging pattern detection)

### Stage 4: Context Matching (Steps 10-12)
- Retrieve agent context (projects, goals, expertise)
- Match post insights to agent focus areas
- Score applicability (0-1)

### Stage 5: Recommendations (Steps 13-15)
- Generate 3 types of recommendations:
  1. **Investigate topic** — workflow improvements to test
  2. **Monitor trend** — watch emerging patterns
  3. **Engage with author** — partnership opportunities
- Include implementation steps + time estimates

### Stage 6: Output (Steps 16-17)
- Serialize to JSON
- Include confidence scores
- Ready for agent interpretation

## Testing

Run test:
```bash
bash pipeline.sh --input-file input/test-posts.json
```

Output: `output/2026-04-29-full-analysis.json`

## Known Limitations

- Sentiment analysis uses simple keyword-based scoring (not ML-based)
- Topic extraction uses predefined keyword matching (not semantic NLP)
- Apify actors may fail on private/deleted posts
- Rate limited by Apify API quotas

## What's Production-Ready

- ✓ Core 17-step pipeline working end-to-end
- ✓ Real Apify post scraping actors integrated
- ✓ Sentiment analysis on actual post content
- ✓ Tested with isolated subagent workflow
- ✓ Error handling for failed scrapes
- ✓ Structured JSON output for agent consumption

## Author

Boris (Skill v2.0-full, 2026-04-29)
