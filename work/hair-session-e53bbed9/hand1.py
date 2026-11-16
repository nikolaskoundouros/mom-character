import bpy
W = bpy.context.window_manager.windows[0]
sc = W.scene
AREA = next(a for a in W.screen.areas if a.type == "VIEW_3D")
REGION = next(r for r in AREA.regions if r.type == "WINDOW")
ob = next(o for o in sc.objects if o.name.startswith("Lock_Top_2_"))
kw = dict(window=W, area=AREA, region=REGION, active_object=ob, object=ob)
with bpy.context.temp_override(**kw):
    for o in sc.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    if ob.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")
sp = ob.data.splines[0]
for i, p in enumerate(sp.points):
    p.select = (i == 4)
bpy.app.driver_namespace["hand_name"] = ob.name
print("lock", ob.name, "mode", ob.mode, "point 4 radius BEFORE", round(sp.points[4].radius, 5), "tilt", round(sp.points[4].tilt, 4))
