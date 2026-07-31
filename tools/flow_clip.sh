#!/bin/bash
# Generate ONE Flow clip end-to-end and save it to disk.
#
#   flow_clip.sh <authuser> <prompt> <output.mp4>
#
# One clip per project, deliberately. Queueing several prompts into one chat session looks like
# it works — each prompt is accepted and the agent answers — but only the first ever produces a
# video; the rest sit there and their approval boxes never arrive. A fresh project answers in
# about ten seconds every time.
#
# Every interaction below is the version that survived a night of ones that didn't:
#   focus   JS el.focus() + a DOM Range. A coordinate click on the prompt box lands on BODY.
#   clear   a real Backspace on that selection. Meta+a does not clear this contenteditable.
#   type    keyboard inserttext. execCommand writes to the DOM but React never sees it, so the
#           send arrow stays dead and both Enter and a click do nothing.
#   click   real mouse move/down/up at the element's rect centre, AFTER scrollIntoView — the
#           chat panel scrolls, and an element above the fold reports a negative y.
#   verify  the prompt box going empty is the only proof a message was sent.
set -u
AB="agent-browser --cdp 9222"
U="$1"; PROMPT="$2"; OUT="$3"

j(){ $AB eval "$1" 2>&1 | tail -1; }
BOX="[...document.querySelectorAll('[contenteditable=\"true\"],textarea')].filter(x=>x.getBoundingClientRect().width>100).pop()"
SEND="[...document.querySelectorAll('button')].filter(x=>((x.getAttribute('aria-label')||'')+(x.textContent||'')).includes('Create')).pop()"
APPROVE="[...document.querySelectorAll('div,span,button')].filter(x=>(x.textContent||'').replace(/\s/g,'')==='checkApprove').pop()"
NEWPROJ="[...document.querySelectorAll('button')].filter(x=>/New project/i.test(x.textContent||'')).pop()"

click(){   # $1 = JS expression returning an element
  local xy
  j "(()=>{const e=$1;if(!e)return 0;e.scrollIntoView({block:'center',inline:'center'});return 1;})()" >/dev/null 2>&1
  sleep 2
  xy=$(j "(()=>{const e=$1;if(!e)return'';const r=e.getBoundingClientRect();if(r.y<0||r.y>innerHeight||r.x<0||r.x>innerWidth)return'';return Math.round(r.x+r.width/2)+' '+Math.round(r.y+r.height/2);})()" | tr -d '"')
  [ -z "$xy" ] && return 1
  $AB mouse move $xy >/dev/null 2>&1
  $AB mouse down    >/dev/null 2>&1
  $AB mouse up      >/dev/null 2>&1
}
boxlen(){ j "(()=>{const e=$BOX;return e?e.innerText.replace('What do you want to create?','').trim().length:-1;})()" | tr -d '"'; }

$AB goto "https://labs.google/fx/tools/flow?authuser=$U" >/dev/null 2>&1; sleep 18
$AB set viewport 1920 1080 >/dev/null 2>&1; sleep 3
click "$NEWPROJ" || { echo "FAIL: no New project button"; exit 1; }
sleep 22
case "$(j '(()=>location.pathname)()')" in
  *project*) : ;;
  *) echo "FAIL: project did not open"; exit 1 ;;
esac

j "(()=>{const e=$BOX;e.focus();const s=getSelection(),r=document.createRange();r.selectNodeContents(e);s.removeAllRanges();s.addRange(r);return 1;})()" >/dev/null 2>&1
$AB press Backspace >/dev/null 2>&1; sleep 1
$AB keyboard inserttext "$PROMPT" >/dev/null 2>&1; sleep 3
[ "$(boxlen)" -lt 80 ] && { echo "FAIL: prompt never reached the box — 0 credits spent"; exit 1; }
click "$SEND"; sleep 8
[ "$(boxlen)" -ge 80 ] && { echo "FAIL: box still full, message not sent — 0 credits spent"; exit 1; }
echo "sent"

for i in $(seq 1 30); do
  sleep 10
  [ "$(j "(()=>[...document.querySelectorAll('div,span,button')].filter(x=>(x.textContent||'').replace(/\s/g,'')==='checkApprove').length)()" | tr -d '"')" -ge 1 ] && break
done
click "$APPROVE" || { echo "FAIL: could not click approve — 0 credits spent"; exit 1; }
echo "approved — 15 credits"

for i in $(seq 1 120); do
  sleep 10
  SRC=$(j "(()=>{const v=document.querySelector('video');return v?(v.currentSrc||v.src||''):'';})()" | tr -d '"')
  [ -n "$SRC" ] && { echo "ready at $((i*10))s"; break; }
done
[ -z "${SRC:-}" ] && { echo "FAIL: no video after 1200s"; exit 1; }

# The <video> src is a tRPC redirect. Following it in the tab lands on a signed
# flow-content.google URL that curl can fetch with no cookies at all.
j "(()=>{const v=document.querySelector('video');const a=document.createElement('a');a.href=v.currentSrc||v.src;a.download='c.mp4';document.body.appendChild(a);a.click();a.remove();return 1;})()" >/dev/null 2>&1
sleep 8
DIRECT=$(j "(()=>location.href)()" | tr -d '"')
case "$DIRECT" in
  *flow-content*) curl -sL -o "$OUT" "$DIRECT" ;;
  *) echo "FAIL: never reached the media URL"; exit 1 ;;
esac
[ -s "$OUT" ] && echo "saved $OUT ($(stat -f%z "$OUT") bytes)" || { echo "FAIL: empty download"; exit 1; }
