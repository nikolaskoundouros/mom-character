"""Seed masks for the outline tool (15 Nov 2026): for every reference camera render (a) OUR HAIR only and (b) OUR BODY only (skin, shirt, collar) as alpha,
so the Mac-side outline tool knows where hair is NOT (face, neck, shirt) and where our hair roughly is. Output /root/live_snaps/vm_hair_<view>.png, vm_body_<view>.png"""
import bpy, json
W = bpy.context.window_manager.windows[0]; sc = W.scene
exec(open("/Users/nick/Desktop/mom-character/live/live_tools.py").read()); gpu_cycles()
J = json.load(open("/Users/nick/Desktop/mom-character/refs/cams.json"))
hairish = lambda o: o.name.startswith(("Lock_", "Hair2_Outer", "Hair2_Fly", "Hair2_Cap"))
bodyish = lambda o: o.name.startswith(("Mom", "Collar", "Placket", "Body"))
objs = [o for o in sc.objects if o.type in ("MESH", "CURVE", "CURVES")]
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 520, 640, 100
sc.cycles.samples = 4; sc.render.film_transparent = True
def set_mode(show):                                   # show = predicate for objects that render; everything else is a holdout (still occludes)
    for o in objs:
        o.is_holdout = not show(o)
for name in J:
    sc.camera = bpy.data.objects[f"RefCam_{name}"]
    set_mode(hairish); sc.render.filepath = f"/root/live_snaps/vm_hair_{name}.png"; bpy.ops.render.render(write_still=True, scene=sc.name)
    saved = {o.name: o.hide_render for o in objs if hairish(o)}
    for o in objs:
        if hairish(o): o.hide_render = True
    set_mode(bodyish); sc.render.filepath = f"/root/live_snaps/vm_body_{name}.png"; bpy.ops.render.render(write_still=True, scene=sc.name)
    for o in objs:
        if o.name in saved: o.hide_render = saved[o.name]
set_mode(lambda o: True); sc.render.film_transparent = False
print("view masks done:", list(J))
