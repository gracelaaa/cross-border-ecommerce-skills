#!/usr/bin/env bash
# ============================================================================
#  daily_reddit.sh — v5 daily fresh Reddit demand-signal scraper (Apify)
# ----------------------------------------------------------------------------
#  Runs the Reddit collector in daily mode (past-24h window, newest-first),
#  stores signals into demand_signals.db, and records run state to
#  reddit_state.json so you can see what was collected each day.
#
#  v5: uses Apify Reddit Scraper Actor ($0.00115/post), no BrowserAct needed.
#  Requires: APIFY_API_TOKEN environment variable
#
#  Install as a WorkBuddy automation (recommended):
#    See automation setup in the project wiki.
#
#  Or as a cron job (runs 09:00 daily):
#    0 9 * * * /bin/bash /path/to/pipeline/daily_reddit.sh >> /path/to/pipeline/reddit_daily.log 2>&1
# ============================================================================
set -u

PIPELINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PIPELINE_DIR" || exit 1

PYTHON="${PYTHON:-/Users/grace/.workbuddy/binaries/python/envs/cross-border/bin/python3}"
RUN_LOG="$PIPELINE_DIR/reddit_daily.log"
STATE_FILE="$PIPELINE_DIR/reddit_state.json"

# ── CLI flags ──────────────────────────────────────────────────────────
# DEEP=1   → force deep-fetch on (already default in v3)
# DEEP=0   → disable deep-fetch for fast runs
# MODE=http → force HTTP-only mode (skip BrowserAct)
# MODE=browser → force BrowserAct-only mode
DEEP_FLAG=""
if [ "${DEEP:-1}" = "0" ]; then
  # Disable deep-fetch (override v3 default)
  DEEP_FLAG=""
elif [ "${DEEP:-1}" = "1" ]; then
  DEEP_FLAG="--deep"
fi

MODE_FLAG=""
case "${MODE:-auto}" in
  http)    MODE_FLAG="--fetch-mode http" ;;
  browser) MODE_FLAG="--fetch-mode browser" ;;
  *)       MODE_FLAG="" ;;  # auto = default
esac

TS="$(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"
echo "[$TS] daily reddit scrape start (v5 Apify)"
echo "  fetch_mode=${MODE:-auto} deep=${DEEP:-1}"
echo "================================================================"

OUT=$("$PYTHON" run.py --only reddit --daily $DEEP_FLAG $MODE_FLAG 2>&1)
echo "$OUT"

# Parse "New: N | Duplicates: M" from run.py output
NEW=$(echo "$OUT" | grep -oE 'New: [0-9]+' | grep -oE '[0-9]+' | head -1)
DUP=$(echo "$OUT" | grep -oE 'Duplicates: [0-9]+' | grep -oE '[0-9]+' | head -1)
NEW="${NEW:-0}"; DUP="${DUP:-0}"

# Update state JSON (append daily line, keep last 30)
python3 - "$STATE_FILE" "$NEW" "$DUP" "${MODE:-auto}" <<'PY'
import sys, json, os, datetime
state_file, new, dup, mode = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
record = {
    "date": datetime.date.today().isoformat(),
    "ran_at": datetime.datetime.now().isoformat(timespec="seconds"),
    "new": int(new),
    "duplicates": int(dup),
    "mode": mode,
    "version": "v5-apify",
}
history = []
if os.path.exists(state_file):
    try:
        history = json.load(open(state_file))
        if isinstance(history, dict):
            history = history.get("history", [])
    except Exception:
        history = []
history.append(record)
history = history[-30:]
json.dump({"last_run": record, "history": history}, open(state_file, "w"),
          indent=2, ensure_ascii=False)
print(f"[state] last_run new={new} dup={dup} mode={mode} -> {state_file}")
PY

echo "[$(date '+%Y-%m-%d %H:%M:%S')] done"
