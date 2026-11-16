"""Hair from scratch, step 1 (15 Nov 2026): shape the Top guides by DATA, not by the Comb brush.
Why: on 15 Nov the real-mouse Comb strokes did not move the guides on the pod (see results.tsv), so the sweep-back is
computed: every guide leaves the scalp, curves back toward the bun position and stays a little above the skin, keeping its
segment length (what Comb does). Run live after the guides exist: exec(open(".../hair2_shape_top.py").read())"""
import math

import bpy
from mathutils import Vector

W = bpy.context.window_manager.windows[0]
sc = W.scene
hair, mom = sc.objects["Hair_Top"], sc.objects["Mom"]
AREA = next(a for a in W.screen.areas if a.type == "VIEW_3D")
REGION = next(r for r in AREA.regions if r.type == "WINDOW")
BUN = Vector((0.0, 0.03, 1.64))                 # my plan: bun centre, high at the back of the crown (reference 62.0 s, 35.0 s)
LIFT0, LIFT1 = 0.010, 0.006                      # my plan: height above the scalp, tuned and recorded
inv = mom.matrix_world.inverted()


def scalp_z(x, y):
    o = inv @ Vector((x, y, 1.9))
    ok, loc, nrm, i = mom.ray_cast(o, inv.to_3x3() @ Vector((0, 0, -1)))
    return (mom.matrix_world @ loc).z if ok else None


kw = dict(window=W, area=AREA, region=REGION, active_object=hair, object=hair)
with bpy.context.temp_override(**kw):
    if hair.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
n = len(hair.data.curves); npt = len(hair.data.points); per = npt // n
buf = [0.0] * (3 * npt)
hair.data.attributes["position"].data.foreach_get("vector", buf)
L = 0.14; step = L / (per - 1)
for c in range(n):
    p = Vector(buf[3 * c * per:3 * c * per + 3])
    out = [p.copy()]
    for k in range(1, per):
        d = (BUN - p).normalized()
        w = 1.0 - k / (per - 1)
        d = (d * (1 - 0.25 * w) + Vector((0, 0, 1)) * 0.25 * w).normalized()
        q = p + d * step
        z0 = scalp_z(q.x, q.y)
        if z0 is not None:
            lim = z0 + LIFT0 + LIFT1 * math.sin(math.pi * k / (per - 1))
            if q.z < lim:
                q.z = lim
        q = p + (q - p).normalized() * step
        out.append(q); p = q
    for k, v in enumerate(out):
        buf[3 * (c * per + k):3 * (c * per + k) + 3] = [v.x, v.y, v.z]
hair.data.attributes["position"].data.foreach_set("vector", buf)
hair.data.update_tag()
with bpy.context.temp_override(**kw):
    bpy.ops.object.mode_set(mode="SCULPT_CURVES")
print("shaped", n, "guides,", per, "points each; mode", hair.mode)
