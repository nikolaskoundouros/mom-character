import bpy
from mathutils import Vector
ns = bpy.app.driver_namespace
sc = WIN.scene if "WIN" in globals() else bpy.context.window_manager.windows[0].scene
W = bpy.context.window_manager.windows[0]
AREA = next(a for a in W.screen.areas if a.type == "VIEW_3D")
REGION = next(r for r in AREA.regions if r.type == "WINDOW")
SPACE = AREA.spaces.active
def ctx(obj=None):
    kw = dict(window=W, area=AREA, region=REGION)
    if obj is not None:
        kw.update(active_object=obj, object=obj)
    return bpy.context.temp_override(**kw)
hair = sc.objects["Hair_Top"]
ov = SPACE.overlay
for a in ("show_bones", "show_extras", "show_floor", "show_axis_x", "show_axis_y", "show_text"):
    if hasattr(ov, a):
        setattr(ov, a, False)
with ctx(hair):
    for o in sc.objects:
        o.select_set(False)
    hair.select_set(True)
    bpy.context.view_layer.objects.active = hair
    bpy.ops.object.mode_set(mode="SCULPT_CURVES")
print("mode:", hair.mode)
try:
    with ctx(hair):
        r = bpy.ops.brush.asset_activate(asset_library_type='ESSENTIALS', relative_asset_identifier='brushes/essentials_brushes-curve_sculpt.blend/Brush/Add')
    print("asset_activate Add:", r)
except Exception as e:
    print("activate failed:", e)
ts = bpy.context.tool_settings
cs = ts.curves_sculpt
b = getattr(cs, "brush", None)
print("brush:", b.name if b else None)
if b:
    print("brush settings props:", [p.identifier for p in b.curves_sculpt_settings.bl_rna.properties if p.identifier not in ("rna_type",)])
    print("size", b.size, "strength", b.strength)
print("curves_sculpt props:", [p.identifier for p in cs.bl_rna.properties if p.identifier not in ("rna_type",)])
print("hair data props:", [p.identifier for p in hair.data.bl_rna.properties if p.identifier in ("use_sculpt_collision","use_sculpt_collision", "surface","surface_uv_map","selection_domain")])
print("curves count:", len(hair.data.curves), "points:", len(hair.data.points))
