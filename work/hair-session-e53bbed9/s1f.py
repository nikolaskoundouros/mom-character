import bpy, json, math
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
W = bpy.context.window_manager.windows[0]
sc = W.scene
AREA = next(a for a in W.screen.areas if a.type == "VIEW_3D")
REGION = next(r for r in AREA.regions if r.type == "WINDOW")
SPACE = AREA.spaces.active
rv3d = SPACE.region_3d
hair, mom = sc.objects["Hair_Top"], sc.objects["Mom"]
def ctx(obj=None):
    kw = dict(window=W, area=AREA, region=REGION)
    if obj is not None:
        kw.update(active_object=obj, object=obj)
    return bpy.context.temp_override(**kw)
with ctx(hair):
    print("activate Comb:", bpy.ops.brush.asset_activate(asset_library_type='ESSENTIALS', relative_asset_identifier='brushes/essentials_brushes-curve_sculpt.blend/Brush/Comb'))
cs = bpy.context.tool_settings.curves_sculpt
cs.brush.size = 90
cs.unified_paint_settings.size = 90
print("brush:", cs.brush.name, cs.brush.size)
# guides now: root and tip
n = len(hair.data.curves)
print("curves", len(hair.data.curves), "points", len(hair.data.points))
# side view from +X (camera at +X looking to -X)
rv3d.view_location = Vector((0.0, -0.06, 1.60))
from mathutils import Matrix
rv3d.view_rotation = Matrix((Vector((0,1,0)), Vector((0,0,1)), Vector((1,0,0)))).transposed().to_quaternion()
rv3d.view_distance = 0.5
rv3d.view_perspective = "PERSP"
bpy.context.view_layer.update()
inv = mom.matrix_world.inverted()
def scr(v):
    c = location_3d_to_region_2d(REGION, rv3d, v)
    return [round(REGION.x + c.x), round(W.height - (REGION.y + c.y))]
def scalp(y, x=0.0):
    o = inv @ Vector((x, y, 1.9)); d = inv.to_3x3() @ Vector((0, 0, -1))
    ok, loc, nrm, i = mom.ray_cast(o, d)
    return (mom.matrix_world @ loc) if ok else None
# profile arc 0.05 above the scalp, from hairline to the bun position
arc = []
for y in [-0.13 + 0.022 * k for k in range(0, 8)]:
    p = scalp(y)
    if p:
        arc.append(scr(Vector((0, y, p.z + 0.05))))
print("ARC", json.dumps(arc))
print("scalp front", scr(scalp(-0.13)), "scalp back", scr(scalp(0.02)))
