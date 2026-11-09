#!/usr/bin/env bash
# Owner-checked dispatch of a background coding-agent job (generic example).
# usage: dispatch.sh <owner> <job_id> <workdir> <prompt_file>
set -euo pipefail
OWNER="$1"; JOB="$2"; WORKDIR="$3"; PROMPT="$4"
HERE="$(cd "$(dirname "$0")" && pwd)"
OWNERS="$HERE/owners.tsv"     # lines: <owner>\t<path prefix>
RUNS="$HERE/runs"
MAX_CONCURRENT=2

# 1. The caller must own the working directory.
if ! awk -F'\t' -v o="$OWNER" -v w="$WORKDIR" '$1==o && index(w,$2)==1 {found=1} END{exit !found}' "$OWNERS"; then
  echo "REFUSE: $WORKDIR is not owned by $OWNER" >&2; exit 4
fi
# 2. Job ids are unique.
[ -e "$RUNS/$JOB" ] && { echo "REFUSE: job id $JOB already used" >&2; exit 5; }
# 3. At most N jobs overall, one per working directory.
running=$(find "$RUNS" -name running -type f 2>/dev/null | wc -l | tr -d ' ')
[ "$running" -ge "$MAX_CONCURRENT" ] && { echo "REFUSE: $running jobs running" >&2; exit 6; }
grep -rlx "$WORKDIR" "$RUNS"/*/workdir_running 2>/dev/null && { echo "REFUSE: workdir busy" >&2; exit 7; }

mkdir -p "$RUNS/$JOB"
echo "$WORKDIR" > "$RUNS/$JOB/workdir_running"; touch "$RUNS/$JOB/running"
(
  # Sandboxed to the working directory, no approval prompts, JSON event log, last message saved.
  coding-agent exec --cd "$WORKDIR" --sandbox workspace-write --json \
      --output-last-message "$RUNS/$JOB/last.md" < "$PROMPT" \
      > "$RUNS/$JOB/events.jsonl" 2> "$RUNS/$JOB/stderr.txt"
  echo $? > "$RUNS/$JOB/exit_code"
  mv "$RUNS/$JOB/running" "$RUNS/$JOB/finished"; mv "$RUNS/$JOB/workdir_running" "$RUNS/$JOB/workdir"
) &
echo "started $JOB"
