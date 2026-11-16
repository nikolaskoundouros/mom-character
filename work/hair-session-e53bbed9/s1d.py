import bpy, json
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
W = bpy.context.window_manager.windows[0]
sc = W.scene
AREA = next(a for a in W.screen.areas if a.type == "VIEW_3D")
REGION = next(r for r in AREA.regions if r.type == "WINDOW")
SPACE = AREA.spaces.active
rv3d = SPACE.region_3d
mom = sc.objects["Mom"]
rv3d.view_location = Vector((0.0, -0.07, 1.62))
rv3d.view_rotation = Vector((0, 0, 1)).to_track_quat("Z", "Y")
rv3d.view_distance = 0.42
rv3d.view_perspective = "PERSP"
bpy.context.view_layer.update()
inv = mom.matrix_world.inverted()
out = []
for x in (0.02, 0.045, 0.07):
    for y in (-0.13, -0.10, -0.07, -0.04, -0.015):
        o = inv @ Vector((x, y, 1.9)); d = inv.to_3x3() @ Vector((0, 0, -1))
        ok, loc, n, i = mom.ray_cast(o, d)
        if not ok:
            continue
        w = mom.matrix_world @ loc
        if w.z < 1.60:
            continue
        c = location_3d_to_region_2d(REGION, rv3d, w)
        out.append([round(x, 3), round(y, 3), round(w.z, 3), round(REGION.x + c.x), round(W.height - (REGION.y + c.y))])
print("GRID", json.dumps(out))
# scalp outline for reference: midline front/back screen positions
for y in (-0.145, 0.02):
    o = inv @ Vector((0, y, 1.9)); d = inv.to_3x3() @ Vector((0, 0, -1))
    ok, loc, n, i = mom.ray_cast(o, d)
    if ok:
        c = location_3d_to_region_2d(REGION, rv3d, mom.matrix_world @ loc)
        print("midline y", y, "screen", round(REGION.x + c.x), round(W.height - (REGION.y + c.y)))
print("curves now:", len(sc.objects["Hair_Top"].data.curves))
