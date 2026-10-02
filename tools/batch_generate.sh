#!/bin/bash
# Generate every clip of one video, one at a time, into /tmp/aica_clips/<key>/
#
#   batch_generate.sh <video_key> <authuser> [start_clip]
#
# One clip per project is deliberate (see flow_clip_v2.sh). Each clip is retried once — Flow's
# chat agent stalls under load often enough that a single failure means nothing.
set -u
KEY="$1"; U="$2"; START="${3:-1}"
ROOT="/tmp/aica_clips/$KEY"
mkdir -p "$ROOT"
cd /Users/beastathome/Desktop/manan/aica

N=$(python3 -c "import sys;sys.path.insert(0,'content/batch2');from videos import VIDEOS;print(len(VIDEOS['$KEY']['shots']))")
echo "=== $KEY: $N clips on authuser=$U ==="

for i in $(seq "$START" "$N"); do
  OUT="$ROOT/c$i.mp4"
  if [ -s "$OUT" ]; then echo "[$i/$N] already have $(stat -f%z "$OUT") bytes — skip"; continue; fi
  P=$(python3 -c "
import sys;sys.path.insert(0,'content/batch2')
from videos import VIDEOS, build
v=VIDEOS['$KEY']; print(build(v['shots'][$i-1], v))")
  echo "[$i/$N] generating..."
  # Retry ONLY when the first attempt died before approving. flow_clip_v2.sh prints
  # "0 credits spent" on every pre-approval failure path; anything else means the generation was
  # already paid for, and blindly retrying would spend another 15 credits on a clip that may well
  # exist in Flow already. Manan's standing rule is that credits are never wasted, so a
  # post-approval failure stops and says so instead.
  LOG="$ROOT/c$i.attempt.log"
  for attempt in 1 2; do
    bash tools/flow_clip_v2.sh "$U" "$P" "$OUT" 2>&1 | tee "$LOG" | sed "s/^/    /"
    [ -s "$OUT" ] && break
    if grep -q "0 credits spent" "$LOG"; then
      echo "    attempt $attempt failed before approving (0 credits) — retrying"
    else
      echo "    attempt $attempt failed AFTER approving — 15 credits already spent, not retrying"
      echo "    the clip may exist in Flow; re-run this one clip by hand rather than regenerating"
      break
    fi
  done
  rm -f "$LOG"
  if [ -s "$OUT" ]; then
    D=$(ffprobe -v error -show_entries stream=width,height -of csv=p=0:s=x "$OUT" 2>/dev/null | head -1)
    echo "[$i/$N] OK $D"
  else
    echo "[$i/$N] GAVE UP"
  fi
done
echo "=== $KEY done: $(ls -1 "$ROOT"/*.mp4 2>/dev/null | wc -l)/$N clips ==="
