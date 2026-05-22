#!/usr/bin/env python3
"""
IG Sales-Technique Extractor

Wraps Apify's instagram-scraper (handle → posts) and apify/instagram-post-scraper
(post URL → full post), then runs Claude analysis tuned for sales-technique
extraction (hooks, frames, CTAs, objection handling, social proof, voice).

Usage:
    python ig-sales-extractor.py @handle1 @handle2 ... --count 20

Output: output/<date>-ig-sales-analysis.json
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

APIFY_TOKEN_PATH = Path.home() / ".config" / "ai-keys" / "apify"
ANTHROPIC_KEY_PATHS = [
    Path.home() / ".config" / "ai-keys" / "anthropic",
    Path.home() / ".anthropic" / "api_key",
]

PROFILE_ACTOR = "apify~instagram-scraper"
POST_ACTOR = "apify~instagram-post-scraper"

SALES_EXTRACTION_PROMPT = """You are analyzing a social media post to extract sales and persuasion techniques. The goal is to build a reusable swipe file of moves a salesperson can replicate.

POST CAPTION:
{caption}

POST METADATA:
- Author: @{author}
- Likes: {likes}
- Comments: {comments}
- Type: {post_type}

Return ONLY valid JSON, no prose. Schema:

{{
  "hook": {{
    "type": "<one of: pattern_interrupt, contrarian, curiosity_gap, stat_shock, story_open, direct_promise, callout, question, social_proof_open, problem_agitation>",
    "verbatim": "<first 1-2 sentences>",
    "why_it_works": "<one sentence>"
  }},
  "frame": {{
    "primary": "<one of: insider_secret, before_after, us_vs_them, framework_reveal, mistake_correction, identity_shift, transformation_story, authority_drop, vulnerability>",
    "tension_promise": "<the gap the post creates and the payoff it offers>"
  }},
  "structure": ["<ordered list of moves: hook -> tension -> proof -> mechanism -> CTA, etc.>"],
  "social_proof": [
    {{"type": "<self_results | client_results | numbers | name_drop | scarcity | authority>", "verbatim": "<exact phrase>"}}
  ],
  "objection_handling": [
    {{"objection_addressed": "<what concern>", "move": "<how they handle it>"}}
  ],
  "cta": {{
    "explicit": <true|false>,
    "type": "<one of: dm_keyword, link_in_bio, comment_prompt, save_share, follow, soft_engagement, none>",
    "verbatim": "<exact CTA text or null>"
  }},
  "voice_signature": {{
    "tone": ["<short tags: punchy, confident, casual, etc.>"],
    "sentence_pattern": "<e.g. short-short-long, list-then-payoff>",
    "signature_devices": ["<e.g. rule-of-three, em-dash punchlines, all-caps emphasis>"]
  }},
  "replicable_template": "<one-paragraph fill-in-the-blank version of the post structure a salesperson could adapt>",
  "fedcon_translation": "<one sentence: how this move could translate to federal contracting consulting voice. null if not applicable>"
}}
"""


def load_token(path: Path, name: str) -> str:
    if not path.exists():
        print(f"ERROR: {name} token not found at {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text().strip()


def load_anthropic_key() -> str:
    for p in ANTHROPIC_KEY_PATHS:
        if p.exists():
            return p.read_text().strip()
    env = os.environ.get("ANTHROPIC_API_KEY")
    if env:
        return env
    print(
        "ERROR: No Anthropic key found in env ANTHROPIC_API_KEY or "
        f"{ANTHROPIC_KEY_PATHS}",
        file=sys.stderr,
    )
    sys.exit(1)


def run_apify_actor(actor: str, input_data: dict, token: str, timeout_s: int = 180) -> list:
    """Start an Apify actor run, poll to completion, return dataset items."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    start = requests.post(
        f"https://api.apify.com/v2/acts/{actor}/runs",
        json=input_data,
        headers=headers,
        timeout=30,
    )
    start.raise_for_status()
    run_id = start.json()["data"]["id"]

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        status = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}",
            headers=headers,
            timeout=15,
        ).json()["data"]
        if status["status"] == "SUCCEEDED":
            items = requests.get(
                f"https://api.apify.com/v2/datasets/{status['defaultDatasetId']}/items",
                headers=headers,
                timeout=30,
            ).json()
            return items
        if status["status"] in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Apify run {run_id} ended with status {status['status']}")
        time.sleep(2)
    raise TimeoutError(f"Apify run {run_id} exceeded {timeout_s}s")


def fetch_profile_posts(handle: str, count: int, token: str) -> list:
    handle = handle.lstrip("@")
    input_data = {
        "directUrls": [f"https://www.instagram.com/{handle}/"],
        "resultsType": "posts",
        "resultsLimit": count,
        "addParentData": False,
    }
    return run_apify_actor(PROFILE_ACTOR, input_data, token)


def analyze_post(post: dict, anthropic_key: str) -> dict:
    caption = post.get("caption") or post.get("text") or ""
    if not caption.strip():
        return {"skipped": True, "reason": "no caption"}

    body = SALES_EXTRACTION_PROMPT.format(
        caption=caption[:4000],
        author=post.get("ownerUsername") or post.get("author") or "unknown",
        likes=post.get("likesCount") or 0,
        comments=post.get("commentsCount") or 0,
        post_type=post.get("type") or "Image",
    )

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": anthropic_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": body}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    text = resp.json()["content"][0]["text"].strip()
    # Strip possible code fences
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json\n"):
            text = text[5:]
        text = text.rsplit("```", 1)[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        return {"error": f"json_parse_failed: {e}", "raw": text[:500]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("handles", nargs="+", help="IG handles (with or without @)")
    parser.add_argument("--count", type=int, default=20, help="Posts per handle (default 20)")
    parser.add_argument("--output-dir", default="output", help="Output dir")
    args = parser.parse_args()

    apify_token = load_token(APIFY_TOKEN_PATH, "Apify")
    anthropic_key = load_anthropic_key()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{datetime.utcnow():%Y-%m-%d}-ig-sales-analysis.json"

    full = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "model": "claude-sonnet-4-6",
        "handles": [],
    }

    for handle in args.handles:
        print(f"[ig-sales] Pulling {args.count} posts from @{handle.lstrip('@')}...", flush=True)
        try:
            posts = fetch_profile_posts(handle, args.count, apify_token)
        except Exception as e:
            print(f"[ig-sales] FAILED to fetch {handle}: {e}", file=sys.stderr)
            full["handles"].append({"handle": handle, "error": str(e), "posts": []})
            continue

        print(f"[ig-sales] Got {len(posts)} posts. Analyzing...", flush=True)
        analyzed = []
        for i, post in enumerate(posts, 1):
            print(f"  [{i}/{len(posts)}] {post.get('shortCode') or post.get('url') or '?'}", flush=True)
            analysis = analyze_post(post, anthropic_key)
            analyzed.append(
                {
                    "url": post.get("url"),
                    "shortcode": post.get("shortCode"),
                    "timestamp": post.get("timestamp"),
                    "caption_preview": (post.get("caption") or "")[:200],
                    "likes": post.get("likesCount"),
                    "comments": post.get("commentsCount"),
                    "type": post.get("type"),
                    "analysis": analysis,
                }
            )
            time.sleep(0.5)  # gentle on Anthropic

        full["handles"].append({"handle": handle, "post_count": len(analyzed), "posts": analyzed})

    out_file.write_text(json.dumps(full, indent=2))
    print(f"[ig-sales] DONE. Wrote {out_file}")


if __name__ == "__main__":
    main()
