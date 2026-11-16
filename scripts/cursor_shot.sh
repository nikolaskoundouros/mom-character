#!/bin/bash
# usage (on the box): cursor_shot.sh "x1,y1 x2,y2 ..."  one held stroke; ffmpeg screen grabs mid-stroke (/root/live_snaps/cs_mid.png) and after release (cs_end.png). STEP=pause between points
cmd='read D A < <(ps -eo args | awk "\$1==\"Xvfb\"{print \$2, \$NF}" | tail -1); export DISPLAY=$D XAUTHORITY=$A; mkdir -p /root/live_snaps; '
STEP=${STEP:-0.06}
pts=($1); n=${#pts[@]}; mid=$((n*2/3))
i=0
for p in "${pts[@]}"; do
  x=${p%,*}; y=${p#*,}
  if [ $i = 0 ]; then cmd+="xdotool mousemove $x $y; sleep 0.15; xdotool mousedown 1; "
  else cmd+="xdotool mousemove $x $y; sleep $STEP; "; fi
  if [ $i = $mid ]; then cmd+="ffmpeg -loglevel error -y -f x11grab -video_size 1920x1080 -i \$DISPLAY -frames:v 1 /root/live_snaps/cs_mid.png; "; fi
  i=$((i+1))
done
cmd+="xdotool mouseup 1; sleep 0.5; ffmpeg -loglevel error -y -f x11grab -video_size 1920x1080 -i \$DISPLAY -frames:v 1 /root/live_snaps/cs_end.png; echo shots done"
cd ~/Desktop/render-desk && ./bin/workbench run "$cmd"
