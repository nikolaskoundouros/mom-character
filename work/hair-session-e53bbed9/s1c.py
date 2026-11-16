import bpy
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
W = bpy.context.window_manager.windows[0]
sc = W.scene
AREA = next(a for a in W.screen.areas if a.type == "VIEW_3D")
REGION = next(r for r in AREA.regions if r.type == "WINDOW")
SPACE = AREA.spaces.active
mom = sc.objects["Mom"]
dg = bpy.context.evaluated_depsgraph_get()
ev = mom.evaluated_get(dg); me = ev.to_mesh()
vs = [mom.matrix_world @ v.co for v in me.vertices if (mom.matrix_world @ v.co).z > 1.52]
xs, ys, zs = [v.x for v in vs], [v.y for v in vs], [v.z for v in vs]
print("verts above z 1.52:", len(vs), "x", round(min(xs), 3), round(max(xs), 3), "y", round(min(ys), 3), round(max(ys), 3), "z", round(min(zs), 3), round(max(zs), 3))
# scalp height profile along the midline and a side line (x=0 and x=0.06), from rays
inv = mom.matrix_world.inverted()
def hit(x, y):
    o = inv @ Vector((x, y, 1.9)); d = inv.to_3x3() @ Vector((0, 0, -1))
    ok, loc, n, i = mom.ray_cast(o, d)
    return (mom.matrix_world @ loc) if ok else None
print("midline x=0 (y: z):", [(round(y, 3), round(hit(0, y).z, 3)) for y in [i * 0.015 - 0.16 for i in range(0, 14)] if hit(0, y)])
print("x=0.06 (y: z):", [(round(y, 3), round(hit(0.06, y).z, 3)) for y in [i * 0.015 - 0.16 for i in range(0, 14)] if hit(0.06, y)])
ev.to_mesh_clear()
