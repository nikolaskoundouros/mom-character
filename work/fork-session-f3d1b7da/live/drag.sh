#!/bin/bash
# usage: drag.sh "x1,y1 x2,y2 ..." [more strokes...]   each argument is one stroke: button held from first to last point
S=/private/tmp/claude-501/-Users-nick/f3d1b7da-7894-44f4-be87-03c3b071e609/scratchpad
cmd='read D A < <(ps -eo args | awk "\$1==\"Xvfb\"{print \$2, \$NF}" | tail -1); export DISPLAY=$D XAUTHORITY=$A; '   # no window activate here: the first press after one is swallowed as a focus click
STEP=${STEP:-0.05}
for stroke in "$@"; do
  first=1
  for p in $stroke; do
    x=${p%,*}; y=${p#*,}
    if [ $first = 1 ]; then cmd+="xdotool mousemove $x $y; sleep 0.15; xdotool mousedown 1; "; first=0
    else cmd+="xdotool mousemove $x $y; sleep $STEP; "; fi
  done
  cmd+="xdotool mouseup 1; sleep 0.25; "
done
cd ~/Desktop/render-desk && ./bin/workbench run "$cmd echo strokes done"
