# IG Sales-Technique Extractor — Setup

Built on top of grandamenium/social-media-insights (Apify scrape layer reused) with a Claude-driven analysis layer tuned for sales-technique extraction.

## What's installed

- `ig-sales-extractor.py` — handle → posts → sales-pattern JSON
- Reuses the upstream `pipeline.sh` Apify scraping pattern but replaces the keyword-sentiment analysis with Claude (claude-sonnet-4-6) returning structured sales output

## Output schema (per post)

```
hook            { type, verbatim, why_it_works }
frame           { primary, tension_promise }
structure       [ ordered moves ]
social_proof    [ { type, verbatim } ]
objection_handling [ { objection_addressed, move } ]
cta             { explicit, type, verbatim }
voice_signature { tone, sentence_pattern, signature_devices }
replicable_template   <fill-in-the-blank version>
fedcon_translation    <how to translate to federal-contracting voice>
```

## Setup (3 steps)

### 1. Get an Apify token (free tier)

1. Sign up: https://console.apify.com/sign-up
2. Account → Settings → API & Integrations → Personal API tokens → copy
3. Save it:

```bash
echo 'YOUR_APIFY_TOKEN' > ~/.config/ai-keys/apify
chmod 600 ~/.config/ai-keys/apify
```

Free tier = $5/mo credit. The `apify/instagram-scraper` actor is ~$2.30 per 1000 results, so $5 ≈ 2000 posts/mo.

### 2. Anthropic key

Already in your env if you've used Claude API before. If not:

```bash
echo 'sk-ant-...' > ~/.config/ai-keys/anthropic
chmod 600 ~/.config/ai-keys/anthropic
```

Or `export ANTHROPIC_API_KEY=...`

### 3. Run it

```bash
cd ~/projects/social-media-insights
python3 ig-sales-extractor.py @handle1 @handle2 --count 20
```

Output → `output/YYYY-MM-DD-ig-sales-analysis.json`

## Cost estimate per run

- 2 accounts × 20 posts = 40 posts
- Apify: ~$0.10
- Claude (sonnet 4.6, ~1.5K tokens in / 1K out per post): ~$0.30
- **Total: ~$0.40 per 40-post run**

## When you're ready

Just paste the two handles. I'll run it and then we can decide whether to (a) compile a swipe-file doc from the JSON, (b) cluster the moves into a reusable framework, or (c) generate FEDCON-translated versions.
