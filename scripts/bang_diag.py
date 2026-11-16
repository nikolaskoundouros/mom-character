import bpy, numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc = bpy.context.window_manager.windows[0].scene; cam = bpy.data.objects["RefCam_q34"]
ref = np.load("/Users/nick/Desktop/mom-character/refs/outline_q34.npy")
def proj(p):
    u, v, _ = world_to_camera_view(sc, cam, Vector(p)); return u * 520, (1 - v) * 640
rows = []
for o in sc.objects:
    if o.name.startswith("Lock_Bang_") and o.type == "CURVE":
        pts = [Vector(o.matrix_world @ Vector(p.co[:3])) for p in o.data.splines[0].points]
        x, y = proj(pts[-1]); xi = int(min(max(x, 0), 519)); col = ref[:, xi]
        ys = np.where(col)[0]; bottom = int(ys.max()) if len(ys) else -1
        rows.append((o.name, round(x), round(y), bottom, round(pts[-1].z, 4)))
rows.sort(key=lambda r: r[1])
print("ours tip px (x,y) | her outline bottom y at that x | tip z")
for r in rows[::3]: print(r)
d = [r[3] - r[2] for r in rows if r[3] > 0]
print("MEAN gap (her bottom - our tip) px:", round(float(np.mean(d)), 1), "over", len(d), "locks")
