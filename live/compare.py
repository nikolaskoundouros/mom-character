"""Reference head crops above, our four head views below, same order: front, 3/4, side-back, back.
Usage: python3 compare.py OURS.png OUT.jpg"""
import sys
from pathlib import Path

import cv2
import numpy as np

d = Path(__file__).resolve().parent
ours = cv2.imread(sys.argv[1])
w = ours.shape[1] // 4
refs = [cv2.imread(str(d.parent / "refs" / "heads" / f"head_{t}.png")) for t in ("64.5", "18.0", "62.0", "35.0")]
top, bot = [], []
for i, r in enumerate(refs):
    o = ours[:, i * w:(i + 1) * w]
    s = 640 / o.shape[0]
    o = cv2.resize(o, (int(o.shape[1] * s), 640))
    r = cv2.resize(r, (o.shape[1], 640))
    cv2.putText(r, "REFERENCE", (8, 620), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(o, "OURS", (8, 620), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    top.append(r); bot.append(o)
cv2.imwrite(sys.argv[2], np.vstack([np.hstack(top), np.hstack(bot)]), [cv2.IMWRITE_JPEG_QUALITY, 88])
