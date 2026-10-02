#!/bin/bash
# Generate every remaining clip of batch 2, one video after another.
#
#   batch_all.sh <authuser> [first_video_key]
#
# Serial on purpose: four of the five Google accounts are still behind Flow's first-run
# onboarding, so there is only one usable account and one browser to drive. Clips that already
# exist on disk are skipped, so this is safe to re-run after any interruption.
set -u
U="${1:-0}"
START="${2:-v1}"
cd /Users/beastathome/Desktop/manan/aica
SEEN=0
for KEY in v1 v2 v3 v4 v5; do
  [ "$KEY" = "$START" ] && SEEN=1
  [ "$SEEN" = "1" ] || continue
  echo ""
  echo "############ $KEY ############"
  bash tools/batch_generate.sh "$KEY" "$U"
done
echo ""
echo "############ ALL DONE ############"
for KEY in v1 v2 v3 v4 v5; do
  N=$(ls -1 /tmp/aica_clips/$KEY/*.mp4 2>/dev/null | wc -l | tr -d ' ')
  W=$(python3 -c "import sys;sys.path.insert(0,'content/batch2');from videos import VIDEOS;print(len(VIDEOS['$KEY']['shots']))")
  echo "$KEY: $N/$W clips"
done
