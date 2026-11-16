#!/bin/bash
# usage: harness.sh BRUSH  (brush asset name: Comb, "Pull Tips", Puff, Pinch, Smooth, Slide, Delete, Add ...)
# One command: rebuild TestSphere + TestHair (fresh every time), enter Curves Sculpt, activate the brush, one REAL held drag with xdotool
# (one press, 31 moves, one release), leave the mode, measure. Fixed 15 Nov 2026: (1) the old build put the strands at x=12 (world coords under a
# parent at x=6) so no brush had anything under it; (2) the old eval passed the 31 points as 31 separate clicks instead of one held drag.
scp -q -o BatchMode=yes ~/Desktop/mom-character/scripts/cursor_harness.py nick@37.27.148.115:Desktop/mom-character/scripts/
B="$1"; WIG=""; [ "$B" = "Smooth" ] && WIG="WIGGLE=1"; [ "$B" = "Slide" ] && WIG="SURFACE_UV=1"; [ -n "$FALLOFF" ] && WIG="$WIG
FALLOFF=\"$FALLOFF\""
call() { ssh -o BatchMode=yes nick@37.27.148.115 "cd ~/Desktop/mom-character && ~/Desktop/render-desk/bin/workbench push ~/Desktop/mom-character >/dev/null 2>&1; python3 live/bcall.py '$WIG
MODE=\"$1\"
BRUSH=\"$B\"
ON_SURFACE=1
exec(open(\"/Users/nick/Desktop/mom-character/scripts/cursor_harness.py\").read())' --timeout 120 2>&1 | tail -3"; }
call build >/dev/null
OUT=$(call prep); echo "$OUT" | grep PREP
ST=$(echo "$OUT" | sed -n 's/^STROKE //p')
ARGS=$(python3 -I -c "
import json
a,b=json.loads('$ST')
print(' '.join('%d,%d'%(a[0]+(b[0]-a[0])*t/30,a[1]+(b[1]-a[1])*t/30) for t in range(31)))")
ssh -o BatchMode=yes nick@37.27.148.115 "cd ~/Desktop/mom-character && STEP=\${STEP:-0.06} live/drag.sh '$ARGS' >/dev/null 2>&1; sleep 4"
call measure | grep RESULT
