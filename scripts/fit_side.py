"""Silhouette fit on the matched reference camera (15 Nov 2026). Globals set by the caller: P_GAP, P_FLARE, P_CURL, P_ZEND (hang parameters), VIEW ('side').
Rebuilds the hair, renders ONLY the hair (everything else is a holdout) from RefCam_<VIEW>, prints IoU against the reference hair polygon."""
import bpy, numpy as np, json
exec(open("/Users/nick/Desktop/mom-character/scripts/hair2_locks.py").read())
W = bpy.context.window_manager.windows[0]; sc = W.scene
exec(open("/Users/nick/Desktop/mom-character/live/live_tools.py").read()); gpu_cycles()
POLY = {"side": [(30,190),(55,150),(110,125),(200,112),(300,125),(345,160),(383,230),(378,285),(335,300),(285,305),(268,340),(255,400),(235,480),(195,530),(130,553),(105,500),(75,380),(65,300),(35,250)]}
v = globals().get("VIEW", "side")
hairish = lambda o: o.name.startswith(("Lock_", "Hair2_Outer", "Hair2_Fly", "Hair2_Cap"))
touched = [o for o in sc.objects if o.type in ("MESH", "CURVE", "CURVES") and not hairish(o) and not o.is_holdout]
for o in touched: o.is_holdout = True
sc.camera = bpy.data.objects[f"RefCam_{v}"]
if globals().get("CAMFILE"):
    from mathutils import Matrix, Vector
    _c = json.load(open(CAMFILE)); sc.camera.data.lens = _c["f_mm"]; sc.camera.matrix_world = Matrix.Translation(Vector(_c["loc"])) @ Matrix(_c["rot"]).to_4x4()
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 520, 640, 100
sc.cycles.samples = 8; sc.render.film_transparent = True; sc.render.filepath = f"/root/live_snaps/fit_{v}.png"
bpy.ops.render.render(write_still=True, scene=sc.name)
for o in touched: o.is_holdout = False
sc.render.film_transparent = False
im = bpy.data.images.load(sc.render.filepath, check_existing=False)
a = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], 4)[::-1, :, 3] > 0.25
import os
_mf = f"/Users/nick/Desktop/mom-character/refs/outline_{v}.npy"
if os.path.exists(_mf) and not globals().get('USE_POLY'):
    inside = np.load(_mf)                                   # accurate outline from outline_auto.py
else:
    ys, xs = np.mgrid[0:640, 0:520]; P = np.array(POLY[v], float); inside = np.zeros((640, 520), bool)
    for i in range(len(P)):
        x1, y1 = P[i]; x2, y2 = P[(i + 1) % len(P)]
        c = ((y1 > ys) != (y2 > ys)) & (xs < (x2 - x1) * (ys - y1) / (y2 - y1 + 1e-9) + x1); inside ^= c
I = (a & inside).sum(); U = (a | inside).sum()
print(f"FIT {v}: IoU={I/U:.3f}  ours_only={(a&~inside).sum()}  ref_only={(~a&inside).sum()}  params gap={P_GAP} flare={P_FLARE} curl={P_CURL} zend={P_ZEND}")
