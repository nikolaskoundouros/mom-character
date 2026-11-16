#!/bin/bash
# usage: pullcmp.sh TAG  -> pulls the live head views from the pod and writes live/TAG_cmp.jpg (reference on top)
S=/private/tmp/claude-501/-Users-nick/f3d1b7da-7894-44f4-be87-03c3b071e609/scratchpad
cd ~/Desktop/render-desk || exit 1
./bin/workbench pull /root/live_snaps $S/live >/dev/null || exit 1
python3 -I - "$S" "$1" <<'PY'
import sys, cv2, numpy as np
S, tag = sys.argv[1], sys.argv[2]
ims = [cv2.imread(f"{S}/live/live_snaps/{tag}_{v}.png") for v in ("hfront", "h34", "hside", "hback")]
cv2.imwrite(f"{S}/live/{tag}_four.png", np.hstack(ims))
PY
python3 -I $S/momhair/compare.py $S/live/${1}_four.png $S/live/${1}_cmp.jpg && echo "$S/live/${1}_cmp.jpg"
