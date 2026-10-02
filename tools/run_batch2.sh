#!/bin/bash
# Generate, verify, assemble and publish every video of batch 2, end to end.
#
#   run_batch2.sh [authuser] [first_video_key]
#
# Serial because only one Google account is currently usable (the other four are still behind
# Flow's first-run onboarding) and there is one browser to drive. Every stage is resumable:
# clips already on disk are skipped, so re-running after any interruption picks up where it left
# off rather than re-spending credits.
set -u
U="${1:-0}"
START="${2:-v1}"
cd /Users/beastathome/Desktop/manan/aica
source .venv/bin/activate
set -a && . ./.env && set +a

SEEN=0
for KEY in v1 v2 v3 v4 v5; do
  [ "$KEY" = "$START" ] && SEEN=1
  [ "$SEEN" = "1" ] || continue

  echo ""
  echo "################ $KEY : generate ################"
  bash tools/batch_generate.sh "$KEY" "$U"

  WANT=$(python3 -c "import sys;sys.path.insert(0,'content/batch2');from videos import VIDEOS;print(len(VIDEOS['$KEY']['shots']))")
  HAVE=$(ls -1 /tmp/aica_clips/$KEY/*.mp4 2>/dev/null | wc -l | tr -d ' ')
  if [ "$HAVE" != "$WANT" ]; then
    echo "!! $KEY has $HAVE/$WANT clips — NOT assembling, moving on"
    continue
  fi

  echo ""
  echo "################ $KEY : verify + assemble + publish ################"
  python3 tools/assemble_batch2.py "$KEY" 2>&1 | grep -v "Fetching\|it/s\]\|%|"
done

echo ""
echo "################ BATCH 2 SUMMARY ################"
for KEY in v1 v2 v3 v4 v5; do
  WANT=$(python3 -c "import sys;sys.path.insert(0,'content/batch2');from videos import VIDEOS;print(len(VIDEOS['$KEY']['shots']))")
  HAVE=$(ls -1 /tmp/aica_clips/$KEY/*.mp4 2>/dev/null | wc -l | tr -d ' ')
  echo "$KEY: $HAVE/$WANT clips"
done
echo "--- library ---"
find library -name final.mp4 -newermt '-1 day' 2>/dev/null | sort
