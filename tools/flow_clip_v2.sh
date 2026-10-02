#!/bin/bash
# Generate ONE Flow clip end-to-end and save it to disk.   (v2 — Sept 2026 Flow rebuild)
#
#   flow_clip_v2.sh <authuser> <prompt> <output.mp4>
#
# WHAT CHANGED vs v1, all of it measured against the live app on 2026-09-05:
#
#   URL          labs.google/fx/tools/flow -> flow.google.com. The old host still redirects,
#                but the redirect drops ?authuser=N, so pass it on the new host directly.
#   clicking     Real CDP mouse move/down/up NO LONGER WORKS. elementFromPoint returns the right
#                button, the coordinates are right, and nothing happens. Tag the node from JS and
#                let `agent-browser click "#id"` do it — that works every time.
#   send         The send control is aria-label="Start generation" (icon text "arrow_forward").
#                v1 looked for a button containing "Create", which matches nothing here, so the
#                prompt sat in the box forever and no clip was ever produced.
#   overlays     A fresh project shows a "Get started" changelog and a "Got it" model tooltip.
#                Both swallow clicks until dismissed.
#   approval     Still not a <button> — it is icon+label text, so it only matches after stripping
#                whitespace ("check"+"Approve"). The chat now also states the price outright:
#                "Would you like me to kick off this 1 video generation, costing 15 credits?"
#   aspect       The Agent-settings 9:16 default did NOT survive into generation — a clip asked
#                for with the default set to 9:16 still came back 1280x720. So the orientation is
#                stated in the prompt instead; the caller is responsible for that line.
#   download     The grid tile is a <video> with NO src until it is played. Click its play_circle,
#                read currentSrc, then let an <a download> click walk the redirect chain: the tab
#                lands on a signed googlevideo.com URL. curl needs a browser UA + Referer + Range,
#                otherwise it returns 0 bytes.
#
# Unchanged and still true: Flow is a React app, so element.click() and execCommand do nothing,
# and Flow's UI is not a source of truth — trust the prompt box emptying, the approval count
# rising, and a file on disk.
#
# Every failure path exits BEFORE approving, so a broken run costs 0 credits.
set -u
AB="agent-browser --cdp 9222"
U="$1"; PROMPT="$2"; OUT="$3"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"

j(){ $AB eval "$1" 2>&1 | tail -1; }

BOX="[...document.querySelectorAll('[contenteditable=\"true\"],textarea')].filter(x=>x.getBoundingClientRect().width>100).pop()"
SEND="[...document.querySelectorAll('button')].filter(x=>/Start generation/i.test(x.getAttribute('aria-label')||'')).pop()"
NEWPROJ="[...document.querySelectorAll('button')].filter(x=>/New project/i.test(x.textContent||'')).pop()"
APPROVE="[...document.querySelectorAll('div,span,button')].filter(x=>(x.textContent||'').replace(/\s/g,'')==='checkApprove').pop()"
PLAY="[...document.querySelectorAll('button,[role=button]')].filter(x=>/play_circle/.test(x.textContent||'')).filter(x=>x.getBoundingClientRect().x<1300)[0]"

click(){   # $1 = JS expression returning an element
  # THE SEPT 2026 FLOW IS ANGULAR, NOT REACT. That single fact retires the rule the old driver was
  # built around. Angular Material listens for real DOM events, so a plain `element.click()` from
  # JS just works — no geometry, no viewport, no focus, no CDP input at all.
  #
  # What was tried first, and why each failed on this UI:
  #   real CDP mouse move/down/up  — the coordinates resolve to the right button and nothing fires
  #   tag + `agent-browser click`  — silently misses when the element's centre is outside the
  #                                  viewport, and the send arrow is pinned to the panel's right
  #                                  edge at x=1896 in a 1920 window
  #   el.focus() + Enter/Space     — focus lands (activeElement confirms it) and the button
  #                                  still does not activate
  # `element.click()` was the last thing tried and the only one that works everywhere.
  j "(()=>{const e=$1;if(!e)return 0;e.scrollIntoView({block:'center',inline:'center'});e.click();return 1;})()" | grep -q 1
}

dismiss(){
  # Any leftover CDK overlay backdrop swallows every click on the page underneath — including
  # "New project", which then reports a cheerful "Done" and does nothing. This is the single most
  # common way a run dies, and it is invisible unless you check for the backdrop directly.
  for L in "Get started" "Got it"; do
    click "[...document.querySelectorAll('button')].filter(x=>/^${L}$/i.test((x.textContent||'').trim())).pop()" >/dev/null 2>&1
    sleep 1
  done
  for attempt in 1 2 3; do
    N=$(j "(()=>document.querySelectorAll('.cdk-overlay-backdrop').length)()" | tr -d '"')
    [ "$N" = "0" ] && break
    $AB press Escape >/dev/null 2>&1
    sleep 1
    j "(()=>{const b=document.querySelector('.cdk-overlay-backdrop');if(b)b.click();return 1;})()" >/dev/null 2>&1
    sleep 1
  done
}

blocked(){   # is anything covering the element this expression returns?
  j "(()=>{const e=$1;if(!e)return 'missing';const r=e.getBoundingClientRect();const el=document.elementFromPoint(Math.round(r.x+r.width/2),Math.round(r.y+r.height/2));return el&&(e===el||e.contains(el))?'clear':'covered';})()" | tr -d '"'
}

boxlen(){ j "(()=>{const e=$BOX;return e?e.innerText.replace('What do you want to create?','').trim().length:-1;})()" | tr -d '"'; }
napprove(){ j "(()=>[...document.querySelectorAll('div,span,button')].filter(x=>(x.textContent||'').replace(/\s/g,'')==='checkApprove').length)()" | tr -d '"'; }

PROJECT="${4:-}"
if [ -n "$PROJECT" ]; then
  $AB goto "$PROJECT" >/dev/null 2>&1; sleep 14
  $AB set viewport 1920 1080 >/dev/null 2>&1; sleep 2
  dismiss
  for i in $(seq 1 15); do
    [ "$(j "(()=>{const e=$BOX;return e?1:0;})()" | tr -d '"')" = "1" ] && break
    sleep 4
  done
  SKIP_CREATE=1
fi
if [ -z "${SKIP_CREATE:-}" ]; then
$AB goto "https://flow.google.com/?authuser=$U" >/dev/null 2>&1; sleep 10
$AB set viewport 1920 1080 >/dev/null 2>&1; sleep 2
# The project list renders a "Loading…" placeholder while it hydrates, and a click that lands
# during it is swallowed — the button is present and focusable, Enter fires, and nothing happens.
# Wait for the placeholder to clear before touching anything.
for i in $(seq 1 20); do
  READY=$(j "(()=>{const t=document.body.innerText;return (!/Loading/i.test(t)&&/New project/i.test(t))?'yes':'no';})()" | tr -d '"')
  [ "$READY" = "yes" ] && break
  sleep 5
done
[ "$READY" != "yes" ] && { echo "FAIL: project list never finished loading — 0 credits spent"; exit 1; }
dismiss
B=$(blocked "$NEWPROJ")
[ "$B" = "covered" ] && { echo "FAIL: New project is covered by an overlay (onboarding not completed on this account?) — 0 credits spent"; exit 1; }
[ "$B" = "missing" ] && { echo "FAIL: no New project button"; exit 1; }
click "$NEWPROJ" || { echo "FAIL: could not click New project"; exit 1; }
for i in $(seq 1 10); do
  sleep 4
  case "$(j '(()=>location.pathname)()')" in *project*) break ;; esac
done
case "$(j '(()=>location.pathname)()')" in
  *project*) : ;;
  *) echo "FAIL: project did not open"; exit 1 ;;
esac
dismiss
for i in $(seq 1 15); do
  [ "$(j "(()=>{const e=$BOX;return e?1:0;})()" | tr -d '"')" = "1" ] && break
  sleep 4
done
fi

# focus + clear: JS focus() and a DOM Range, then a real Backspace. A coordinate click on the
# prompt box lands on BODY, and Meta+a does not clear this contenteditable.
j "(()=>{const e=$BOX;if(!e)return 0;e.focus();const s=getSelection(),r=document.createRange();r.selectNodeContents(e);s.removeAllRanges();s.addRange(r);return 1;})()" >/dev/null 2>&1
$AB press Backspace >/dev/null 2>&1; sleep 1
$AB keyboard inserttext "$PROMPT" >/dev/null 2>&1; sleep 3

LEN=$(boxlen)
[ "$LEN" -lt 80 ] && { echo "FAIL: prompt never reached the box (len=$LEN) — 0 credits spent"; exit 1; }
# the send arrow stays disabled until React actually holds the text — the only proof it landed
DIS=$(j "(()=>{const e=$SEND;return e?String(e.disabled):'missing';})()" | tr -d '"')
[ "$DIS" != "false" ] && { echo "FAIL: send arrow is '$DIS' — prompt did not register, 0 credits spent"; exit 1; }

BEFORE=$(napprove)
click "$SEND"; sleep 8
[ "$(boxlen)" -ge 80 ] && { echo "FAIL: box still full, message not sent — 0 credits spent"; exit 1; }
echo "sent"

for i in $(seq 1 30); do
  sleep 10
  [ "$(napprove)" -gt "$BEFORE" ] && break
done
[ "$(napprove)" -le "$BEFORE" ] && { echo "FAIL: no approval box after 300s — 0 credits spent"; exit 1; }
echo "cost: $(j "(()=>{const m=document.body.innerText.match(/costing ([0-9]+) credits/);return m?m[1]:'?';})()" | tr -d '"') credits"

click "$APPROVE" || { echo "FAIL: could not click approve — 0 credits spent"; exit 1; }
echo "approved"

# Getting the finished clip off the page took three wrong turns:
#   * `document.querySelector("video")` finds nothing — the grid tile renders as an <img> poster
#   * clicking its play_circle does not swap it either
#   * filtering tiles by `width > 200` misses them completely, because a 9:16 tile is NARROW
#     (141x250). Discriminate by x instead: grid cards sit left of centre, the chat thumbnail is
#     ~192px at x>1500.
# What actually works: dispatch a hover over the tile. That swaps the poster for a real <video>
# carrying its src.
SRC=""
for i in $(seq 1 90); do
  sleep 10
  j "(()=>{const i=[...document.querySelectorAll('img')].filter(x=>{const r=x.getBoundingClientRect();return r.x<1300&&r.height>100;})[0];if(!i)return 0;const c=i.closest('div');['mouseover','mouseenter','mousemove'].forEach(e=>c.dispatchEvent(new MouseEvent(e,{bubbles:true})));return 1;})()" >/dev/null 2>&1
  sleep 3
  SRC=$(j "(()=>{const v=[...document.querySelectorAll('video')].find(v=>v.currentSrc||v.src);return v?(v.currentSrc||v.src):'';})()" | tr -d '"')
  [ -n "$SRC" ] && { echo "clip ready at ~$((i*13))s"; break; }
done
[ -z "$SRC" ] && { echo "FAIL: clip never appeared (credits already spent)"; exit 1; }

DIM=$(j "(()=>{const v=[...document.querySelectorAll('video')].find(v=>v.currentSrc||v.src);return v.videoWidth+'x'+v.videoHeight;})()" | tr -d '"')
echo "dimensions: $DIM"
case "$DIM" in
  720x1280|1080x1920) : ;;
  *) echo "WARNING: $DIM is not portrait — the prompt's orientation line may have been ignored" ;;
esac

# currentSrc is an authenticated endpoint; an <a download> click walks the redirect chain and
# leaves the tab on a signed URL that curl can fetch — but only with a browser UA, a Referer and
# a Range header. Without them it writes 0 bytes and ffprobe reports "moov atom not found".
j "(()=>{const v=[...document.querySelectorAll('video')].find(v=>v.currentSrc||v.src);const a=document.createElement('a');a.href=v.currentSrc||v.src;a.download='c.mp4';document.body.appendChild(a);a.click();a.remove();return 1;})()" >/dev/null 2>&1
sleep 9
DIRECT=$(j "(()=>location.href)()" | tr -d '"')
case "$DIRECT" in
  *googlevideo*|*flow-content*)
    mkdir -p "$(dirname "$OUT")"
    curl -sL --max-time 180 -H "User-Agent: $UA" -H "Referer: https://flow.google.com/" \
         -H "Range: bytes=0-" -o "$OUT" "$DIRECT" ;;
  *) echo "FAIL: never reached the media URL (got ${DIRECT:0:60})"; exit 1 ;;
esac
[ -s "$OUT" ] && echo "saved $OUT ($(stat -f%z "$OUT") bytes, $DIM)" || { echo "FAIL: empty download"; exit 1; }
