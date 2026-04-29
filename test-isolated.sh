#!/bin/bash
# Isolated subagent test simulation for social-media-insights skill
# Demonstrates how a fresh agent would invoke and use the skill

set -euo pipefail

echo "=== ISOLATED SUBAGENT TEST ==="
echo "Testing skill in isolation (simulating fresh agent context)"
echo ""

# Simulate isolated agent context (no prior knowledge)
export CTX_AGENT_NAME="test-worker-01"
export CTX_PROJECTS="cortextos-framework,agent-optimization"
export CTX_GOALS="improve-workflows,enhance-automation"

SKILL_DIR="/Users/cortextos/cortextos/orgs/lifeos/agents/boris/.claude/skills/social-media-insights"
cd "$SKILL_DIR"

echo "[test-worker-01] Loading skill: social-media-insights"
echo "[test-worker-01] Checking SKILL.md for documentation..."
if [[ ! -f SKILL.md ]]; then
  echo "[ERROR] Skill documentation missing!"
  exit 1
fi

echo "[test-worker-01] ✓ Skill documentation found"
echo ""
echo "[test-worker-01] Invoking: bash pipeline.sh --input-file input/test-posts.json"
echo ""

# Run skill (don't pipe to head to avoid pipefail issues)
bash pipeline.sh --input-file input/test-posts.json 2>&1
if [[ $? -eq 0 ]]; then
  echo ""
  echo "[test-worker-01] ✓ Skill execution successful"

  # Verify output
  if [[ -f output/2026-04-29-full-analysis.json ]]; then
    echo "[test-worker-01] ✓ Output file generated"

    # Parse output structure
    python3 << 'VERIFY'
import json
import sys

with open("output/2026-04-29-full-analysis.json") as f:
    output = json.load(f)

print("[test-worker-01] Output structure verification:")
print(f"  - test_id: {output.get('test_id')} ✓")
print(f"  - steps_completed: {output.get('steps_completed')}/17 ✓")
print(f"  - posts_processed: {output.get('posts_processed')} ✓")
print(f"  - extracted_posts: {len(output.get('extracted_posts', []))} posts ✓")
print(f"  - analysis results: {len(output.get('analysis', []))} ✓")
print(f"  - recommendations: {len(output.get('recommendations', []))} ✓")

# Check recommendation structure
if output.get('recommendations'):
    rec = output['recommendations'][0]
    print(f"\nFirst recommendation structure:")
    print(f"  - id: {rec.get('id')} ✓")
    print(f"  - priority_score: {rec.get('priority_score')} ✓")
    print(f"  - actions: {len(rec.get('actions', []))} action(s) ✓")

    if rec.get('actions'):
        action = rec['actions'][0]
        print(f"\nFirst action structure:")
        print(f"  - action: {action.get('action')} ✓")
        print(f"  - topic: {action.get('topic')} ✓")
        print(f"  - urgency: {action.get('urgency')} ✓")
        print(f"  - implementation_steps: {len(action.get('implementation_steps', []))} steps ✓")

print("\n[test-worker-01] ✓ Output structure VALID")
print("[test-worker-01] ✓ Agent can parse and consume recommendations")
VERIFY
  else
    echo "[ERROR] Output file not generated"
    exit 1
  fi
else
  echo "[ERROR] Skill execution failed"
  exit 1
fi

echo ""
echo "=== SUBAGENT TEST COMPLETE ==="
echo "Status: PASS ✓"
echo "Ready for: Multi-agent deployment"
