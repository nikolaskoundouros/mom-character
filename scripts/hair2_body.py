"""Hair from scratch (15 Nov 2026), step 0: her body and outfit in the live pod Blender, NO hair.
Same live-scene setup as rebuild_live.py (it only differs in skipping every hair builder), so a fresh pod gets the same body.
Run inside the live Blender with: exec(open("/Users/nick/Desktop/mom-character/scripts/hair2_body.py").read())"""
import os
import sys
import time

import bpy

L = "/Users/nick/Desktop/mom-character"
for p in ("/Users/nick/Desktop/blender-funnel", f"{L}/scripts"):
    if p not in sys.path:
        sys.path.insert(0, p)
exec(open(f"{L}/live/live_tools.py").read())
from recipes import stage  # noqa: E402
import mom_hair  # noqa: E402

mom_hair.half_up_bun = lambda *a, **k: {}      # the old hair builder is history: no hair at all

KNOBS = dict(ROOM=0.6, CAP_MIN=0.92, RED=0.55, TEX=0.6)
os.environ.update({k: str(v) for k, v in KNOBS.items()})
os.environ["HAIR"] = "scratch"                  # mom.py's "no ponytail asset" branch; bangs stay off (BANGS defaults to 0)


def live_new_scene():
    sc = WIN.scene
    for o in list(sc.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    return sc


stage.new_scene = live_new_scene
t = time.time()
src = open(f"{L}/scripts/mom.py").read().split('if os.environ.get("NO_RENDER"):')[0]
old = sys.argv
sys.argv = ["mom.py"]
try:
    with bpy.context.temp_override(window=WIN, screen=WIN.screen, scene=WIN.scene):
        exec(compile(src, f"{L}/scripts/mom.py", "exec"), {"__file__": f"{L}/scripts/mom.py", "__name__": "__live__"})
finally:
    sys.argv = old
print(f"body built in {time.time() - t:.0f} s;", len(WIN.scene.objects), "objects")
for o in WIN.scene.objects:
    print(" ", o.name, o.type, len(o.data.vertices) if o.type == "MESH" else "")
