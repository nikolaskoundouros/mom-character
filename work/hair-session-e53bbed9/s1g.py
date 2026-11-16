import bpy, json
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
W = bpy.context.window_manager.windows[0]
sc = W.scene
AREA = next(a for a in W.screen.areas if a.type == "VIEW_3D")
REGION = next(r for r in AREA.regions if r.type == "WINDOW")
SPACE = AREA.spaces.active
rv3d = SPACE.region_3d
hair, mom = sc.objects["Hair_Top"], sc.objects["Mom"]
cs = bpy.context.tool_settings.curves_sculpt
cs.brush.size = 70; cs.unified_paint_settings.size = 70
n = len(hair.data.curves); npt = len(hair.data.points); per = npt // n
buf = [0.0] * (3 * npt)
hair.data.attributes["position"].data.foreach_get("vector", buf)
P = [Vector(buf[3 * i:3 * i + 3]) for i in range(npt)]
inv = mom.matrix_world.inverted()
def scr(v):
    c = location_3d_to_region_2d(REGION, rv3d, v)
    return [round(REGION.x + c.x), round(W.height - (REGION.y + c.y))]
def scalp(x, y):
    o = inv @ Vector((x, y, 1.9)); d = inv.to_3x3() @ Vector((0, 0, -1))
    ok, loc, nrm, i = mom.ray_cast(o, d)
    return (mom.matrix_world @ loc) if ok else None
rows = {}
for c in range(n):
    pts = P[c * per:(c + 1) * per]
    rows.setdefault(round(pts[0].y, 2), []).append(pts)
strokes = []
for y in sorted(rows):
    pts = rows[y][0]
    R = pts[0]
    mid, tip = pts[per // 2], pts[-1]
    def tgt(dy, h):
        s = scalp(R.x * 0.6, min(R.y + dy, 0.02))
        return Vector((R.x * 0.6, min(R.y + dy, 0.02), (s.z if s else R.z) + h))
    pairs = [(mid, tgt(0.055, 0.014)), (tip, tgt(0.11, 0.024))]
    for a, b in pairs:
        sa, sb = scr(a), scr(b)
        path = [[round(sa[0] + (sb[0] - sa[0]) * t / 5), round(sa[1] + (sb[1] - sa[1]) * t / 5)] for t in range(6)]
        strokes.append(path)
    print("row y", y, "root", tuple(round(c, 3) for c in R), "tip", tuple(round(c, 3) for c in tip), "n", len(rows[y]))
print("STROKES", json.dumps(strokes))
