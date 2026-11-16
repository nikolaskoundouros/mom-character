"""One call rebuilds her in a fresh live pod Blender with the current best settings (14 Nov):
body and outfit (mom.py), code-built top / bangs / pieces / bun (mom_hair.py), and the lower hair the tutorial's way
(live_dyn.py: particle hair + interpolated children + Hair Dynamics). The gravity simulation is run separately
(frame by frame, in short calls) so no single connector call times out."""
import os
import sys
import time

import bpy

L = "/private/tmp/claude-501/-Users-nick/f3d1b7da-7894-44f4-be87-03c3b071e609/scratchpad/podsync"
for p in ("/Users/nick/Desktop/blender-funnel", f"{L}/mom"):
    if p not in sys.path:
        sys.path.insert(0, p)
exec(open(f"{L}/live/live_tools.py").read())
from recipes import stage  # noqa: E402

KNOBS = dict(ROOM=0.6, CAP_MIN=0.92, RED=0.55, MEL_BUN=0.7, TEX=0.6, PART=0.0015,
             BANG_END0=0.012, BANG_W=0.055, N_BANG=9000, BANG_SWEEP=0.35, BANG_OUT=0.08, MEL_STREAK=0.22,
             PIECE_END=-0.03, N_PIECE=1500, CLUMP_PIECE=0.85,
             VOL=0.018, HAIR_RADIUS=0.00011, N_TOP=60000, ROOT_TOP=0.04, BLEND=0.015,
             MEL=0.38, MEL_TOP=0.34, MEL_LOW=0.44, BUN_TWIST=13.0, BUN_FRIZZ=0.0018,
             N_LOW=200, G_LOW=40)


def live_new_scene():
    sc = WIN.scene
    for o in list(sc.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    return sc


stage.new_scene = live_new_scene
os.environ.update({k: str(v) for k, v in KNOBS.items()})
t = time.time()
src = open(f"{L}/mom/mom.py").read().split('if os.environ.get("NO_RENDER"):')[0]
old = sys.argv
sys.argv = ["mom.py"]
try:
    with bpy.context.temp_override(window=WIN, screen=WIN.screen, scene=WIN.scene):
        exec(compile(src, f"{L}/mom/mom.py", "exec"), {"__file__": f"{L}/mom/mom.py", "__name__": "__live__"})
finally:
    sys.argv = old
low = bpy.data.objects.get("Hair_lower")
if low:
    bpy.data.objects.remove(low, do_unlink=True)
exec(compile(open(f"{L}/mom/live_dyn.py").read(), f"{L}/mom/live_dyn.py", "exec"), {"__name__": "__live__"})
WIN.scene.frame_start, WIN.scene.frame_end = 1, 60
WIN.scene.frame_set(1)
print(f"rebuilt in {time.time() - t:.0f} s;", len(WIN.scene.objects), "objects")
