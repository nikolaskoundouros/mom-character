"""OUTLINE TOOL (15 Nov 2026). Accurate hair mask of a reference frame with no hand-drawn polygon.
Seeds come from OUR OWN render at the matched camera: core of our hair = definitely hair; far from our hair = definitely not; our body (skin, neck, shirt) where our hair
is absent = definitely not hair; letterbox and caption = not hair. GrabCut then decides the uncertain band by colour in HER frame.
usage: python3 outline_auto.py VIEW  ->  ana_out/outline_<view>.png (mask), outline_<view>_check.jpg"""
import cv2, numpy as np, sys, json, os
S = "/private/tmp/claude-501/-Users-nick/e53bbed9-cca3-49b0-bf6a-b54722760597/scratchpad"; VM = f"{S}/vm"; OUT = f"{S}/ana"
R = "/Users/nick/Desktop/mom-character/refs/heads"
J = json.load(open("/Users/nick/Desktop/mom-character/refs/cams.json"))

PARAMS = {"side": dict(band_out=40, body_top=0), "q34": dict(band_out=95, body_top=345), "front": dict(band_out=75, body_top=350), "back": dict(band_out=60, body_top=0)}


def run(view, band_out=None, core_in=22, iters=10, body_top=None):
    band_out = band_out or PARAMS[view]["band_out"]; body_top = PARAMS[view]["body_top"] if body_top is None else body_top
    ref = cv2.imread(f"{R}/{J[view]['img']}")
    H = cv2.imread(f"{VM}/vm_hair_{view}.png", cv2.IMREAD_UNCHANGED)[..., 3] > 100
    B = cv2.imread(f"{VM}/vm_body_{view}.png", cv2.IMREAD_UNCHANGED)[..., 3] > 100
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    Hu = H.astype(np.uint8)
    far = cv2.dilate(Hu, k(band_out)) == 0
    core = cv2.erode(Hu, k(core_in)) > 0
    Bc = B.copy(); Bc[:body_top] = False                                    # her bangs cover the forehead: only face/neck BELOW the eyes count as non-hair
    body_bg = cv2.erode((Bc & ~(cv2.dilate(Hu, k(8)) > 0)).astype(np.uint8), k(4)) > 0
    junk = (ref.max(axis=2) < 14)                                              # letterbox
    junk[:36, :310] = True                                                     # yellow caption
    gc = np.full(ref.shape[:2], cv2.GC_PR_BGD, np.uint8)
    gc[cv2.dilate(Hu, k(10)) > 0] = cv2.GC_PR_FGD
    gc[far | junk] = cv2.GC_BGD; gc[body_bg] = cv2.GC_BGD; gc[core & ~body_bg] = cv2.GC_FGD
    bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
    cv2.grabCut(ref, gc, None, bg, fg, iters, cv2.GC_INIT_WITH_MASK)
    m = ((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k(2)); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k(5))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)                         # keep the largest piece
    if n > 1: m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    m = cv2.medianBlur(m * 255, 7) > 127
    return ref, m, H, B

if __name__ == "__main__":
    view = sys.argv[1]; ref, m, H, B = run(view)
    cv2.imwrite(f"{OUT}/outline_{view}.png", m.astype(np.uint8) * 255)
    vis = ref.copy(); cnt, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    shade = vis.copy(); shade[~m] = (shade[~m] * 0.35).astype(np.uint8)
    cv2.drawContours(shade, cnt, -1, (0, 255, 255), 2)
    ours = np.zeros_like(ref); ours[H] = (0, 0, 255)
    cv2.imwrite(f"{OUT}/outline_{view}_check.jpg", np.hstack([ref, shade, cv2.addWeighted(ref, 0.6, ours, 0.4, 0)]))
    print(view, "hair px", int(m.sum()))
