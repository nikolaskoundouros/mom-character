"""Hair flow map: which way the strands run at each point, from a bank of Gabor filters
(the orientation-map step used by the image-to-hair papers, e.g. HairStep / Im2Haircut preprocessing).
Draws a short line per grid cell in the strongest local strand direction, only where the texture is
clearly striped (hair), coloured by direction so mismatches stand out.
Usage: python3 flowmap.py OUT.jpg TOP1.png TOP2.png ... -- BOTTOM1.png ...   (rows of equal-height tiles)"""
import sys

import cv2
import numpy as np

ANGLES = np.deg2rad(np.arange(0, 180, 7.5))
KERNELS = [cv2.getGaborKernel((17, 17), 2.4, a, 5.0, 0.5, 0, ktype=cv2.CV_32F) for a in ANGLES]


def orientation(gray):
    g = gray.astype(np.float32) / 255.0
    resp = np.stack([np.abs(cv2.filter2D(g, cv2.CV_32F, k)) for k in KERNELS])
    best = resp.argmax(0)
    conf = resp.max(0) - np.median(resp, 0)                   # striped texture: one angle wins clearly
    # Gabor theta is the normal of the stripes; the strand runs at theta + 90 deg
    theta = ANGLES[best] + np.pi / 2
    # average directions locally as doubled angles (a line has no head or tail)
    c = cv2.GaussianBlur(np.cos(2 * theta) * conf, (0, 0), 4)
    s = cv2.GaussianBlur(np.sin(2 * theta) * conf, (0, 0), 4)
    return 0.5 * np.arctan2(s, c), cv2.GaussianBlur(conf, (0, 0), 4)


def draw(img, step=13):
    out = (img * 0.55).astype(np.uint8)
    theta, conf = orientation(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hair = (hsv[..., 0] >= 5) & (hsv[..., 0] <= 28) & (hsv[..., 1] > 60) & (hsv[..., 2] > 50)   # honey hues, not white shirt or dark room
    hair[:40] = False                                                                             # the label box
    hair = cv2.morphologyEx(hair.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    thr = 0.30 * np.percentile(conf, 99.5)                  # clearly striped only: flat walls and smooth skin drop out
    for y in range(step // 2, img.shape[0], step):
        for x in range(step // 2, img.shape[1], step):
            if not hair[y, x] or conf[y, x] < thr:
                continue
            t = theta[y, x]
            dx, dy = np.cos(t) * step * 0.55, np.sin(t) * step * 0.55
            hue = int((np.degrees(t) % 180))                   # OpenCV hue 0..179 = line direction
            col = cv2.cvtColor(np.uint8([[[hue, 255, 255]]]), cv2.COLOR_HSV2BGR)[0, 0].tolist()
            cv2.line(out, (int(x - dx), int(y - dy)), (int(x + dx), int(y + dy)), col, 2, cv2.LINE_AA)
    return out


def row(paths, h=640):
    tiles = []
    for p in paths:
        im = cv2.imread(p)
        im = cv2.resize(im, (int(im.shape[1] * h / im.shape[0]), h))
        tiles.append(draw(im))
    return np.hstack(tiles)


args = sys.argv[2:]
cut = args.index("--") if "--" in args else len(args)
rows = [row(args[:cut])] + ([row(args[cut + 1:])] if cut < len(args) else [])
w = max(r.shape[1] for r in rows)
rows = [np.hstack([r, np.zeros((r.shape[0], w - r.shape[1], 3), np.uint8)]) if r.shape[1] < w else r for r in rows]
key = np.full((70, w, 3), 20, np.uint8)
for i, (deg, name) in enumerate([(90, "straight down"), (45, "slant"), (0, "sideways"), (135, "other slant")]):
    col = cv2.cvtColor(np.uint8([[[deg, 255, 255]]]), cv2.COLOR_HSV2BGR)[0, 0].tolist()
    t = np.radians(deg); x0 = 40 + i * 360
    cv2.line(key, (int(x0 - 18 * np.cos(t)), int(35 - 18 * np.sin(t))), (int(x0 + 18 * np.cos(t)), int(35 + 18 * np.sin(t))), col, 4, cv2.LINE_AA)
    cv2.putText(key, name, (x0 + 32, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (230, 230, 230), 2)
cv2.imwrite(sys.argv[1], np.vstack(rows + [key]), [cv2.IMWRITE_JPEG_QUALITY, 90])
