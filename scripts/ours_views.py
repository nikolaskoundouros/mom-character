# our four reference-matched views at 520x640: normal render + hair-only RGBA mask
import bpy
from mathutils import Vector
exec(open("/Users/nick/Desktop/mom-character/live/live_tools.py").read())
sc = WIN.scene; gpu_cycles()
body = [o for o in sc.objects if o.type == "MESH" and o.name.startswith("Mom")]
top = max((o.matrix_world @ Vector(c)).z for o in body for c in o.bound_box)
V = {"hfront": (0.05, -0.95, top - 0.08), "h34": (-0.62, -0.70, top - 0.08), "hside": (-0.88, 0.30, top - 0.06), "hback": (0.15, 0.95, top - 0.05)}
aim = Vector((0.0, 0.0, top - 0.13))
cam = bpy.data.objects.get("LiveCam"); sc.camera = cam; cam.data.lens = 70.0
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 520, 640, 100
sc.cycles.samples = 48
def go(tag):
    for k, loc in V.items():
        cam.location = loc; cam.rotation_euler = (aim - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = f"/root/live_snaps/cmp_{tag}_{k}.png"; bpy.ops.render.render(write_still=True, scene=sc.name)
go("rgb")
hairish = lambda o: o.name.startswith(("Lock_", "Hair2_Outer", "Hair2_Fly", "Hair2_Cap"))
touched = []
for o in sc.objects:
    if o.type in ("MESH", "CURVE", "CURVES") and not hairish(o):
        o.is_holdout = True; touched.append(o)           # body, shirt, floor: holdout = transparent in alpha but still hides hair behind them
sc.render.film_transparent = True
sc.render.image_settings.color_mode = "RGBA"
sc.cycles.samples = 16
go("mask")
sc.render.film_transparent = False
for o in touched:
    o.is_holdout = False
print("matched views done")
