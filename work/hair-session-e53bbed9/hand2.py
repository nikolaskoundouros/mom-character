import bpy
W = bpy.context.window_manager.windows[0]
sc = W.scene
A = next(a for a in W.screen.areas if a.type == "VIEW_3D"); R = next(r for r in A.regions if r.type == "WINDOW")
ob = next(o for o in sc.objects if o.name.startswith("Lock_Low_-1_") and o.name.endswith("_1.615") or o.name.startswith("Lock_Low_-1_") and "_1.6" in o.name)
with bpy.context.temp_override(window=W, area=A, region=R, active_object=ob, object=ob):
    for o in sc.objects: o.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
sp = ob.data.splines[0]
for i, p in enumerate(sp.points): p.select = i in (0, 1)
bpy.app.driver_namespace["hand_name"] = ob.name
print(ob.name, "radius pts 0..3 BEFORE", [round(sp.points[i].radius, 5) for i in range(4)])
