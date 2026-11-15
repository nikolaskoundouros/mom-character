#!/bin/bash
# usage: live/pullcmp.sh TAG -> pulls the live head views from the pod into live/live_snaps and writes live/TAG_cmp.jpg (reference on top)
P="$(cd "$(dirname "$0")/.." && pwd)"
cd ~/Desktop/render-desk || exit 1
./bin/workbench pull /root/live_snaps "$P/live" >/dev/null || exit 1
python3 -I - "$P" "$1" <<'PY'
import sys, cv2, numpy as np
P, tag = sys.argv[1], sys.argv[2]
ims = [cv2.imread(f"{P}/live/live_snaps/{tag}_{v}.png") for v in ("hfront", "h34", "hside", "hback")]
cv2.imwrite(f"{P}/live/{tag}_four.png", np.hstack(ims))
PY
python3 -I "$P/live/compare.py" "$P/live/${1}_four.png" "$P/live/${1}_cmp.jpg" && echo "$P/live/${1}_cmp.jpg"
