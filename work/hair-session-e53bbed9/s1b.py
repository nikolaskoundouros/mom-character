import bpy, json
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
W = bpy.context.window_manager.windows[0]
sc = W.scene
AREA = next(a for a in W.screen.areas if a.type == "VIEW_3D")
REGION = next(r for r in AREA.regions if r.type == "WINDOW")
SPACE = AREA.spaces.active
hair, mom = sc.objects["Hair_Top"], sc.objects["Mom"]
cs = bpy.context.tool_settings.curves_sculpt
b = cs.brush
s = b.curves_sculpt_settings
s.add_amount = 1
s.curve_length = 0.14
s.points_per_curve = 10
s.curve_radius = 0.0002
s.use_length_interpolate = False
s.use_shape_interpolate = False
s.use_point_count_interpolate = False
s.use_radius_interpolate = False
b.size = 12
hair.data.use_sculpt_collision = True
cs.use_symmetry_x = True
print("brush set:", b.name, s.add_amount, s.curve_length, s.points_per_curve, "size", b.size, "collision", hair.data.use_sculpt_collision, "symX", cs.use_symmetry_x)
# top-down view on the crown
rv3d = SPACE.region_3d
rv3d.view_location = Vector((0.0, -0.01, 1.62))
rv3d.view_rotation = Vector((0, 0, 1)).to_track_quat("Z", "Y")
rv3d.view_distance = 0.55
rv3d.view_perspective = "PERSP"
bpy.context.view_layer.update()
inv = mom.matrix_world.inverted()
pts = []
for x in (0.02, 0.05, 0.075):
    for y in (-0.07, -0.045, -0.02, 0.005, 0.03, 0.055):
        o = inv @ Vector((x, y, 1.9)); d = (inv.to_3x3() @ Vector((0, 0, -1)))
        ok, loc, nrm, idx = mom.ray_cast(o, d)
        if ok:
            w = mom.matrix_world @ loc
            c = location_3d_to_region_2d(REGION, rv3d, w)
            pts.append((round(x, 3), round(y, 3), round(w.z, 3), round(REGION.x + c.x), round(W.height - (REGION.y + c.y))))
print("region", REGION.x, REGION.y, REGION.width, REGION.height, "window", W.width, W.height)
print("grid (x, y, z, screenX, screenY):")
for p in pts:
    print(p)
