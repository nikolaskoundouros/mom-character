import bpy, math
from mathutils import Vector
exec(open("/Users/nick/Desktop/mom-character/live/live_tools.py").read())
sc = WIN.scene
gpu_cycles()
cam = bpy.data.objects.get("LiveCam")
if cam is None:
    cam = bpy.data.objects.new("LiveCam", bpy.data.cameras.new("LiveCam")); sc.collection.objects.link(cam)
sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 800, 1000, 100
sc.cycles.samples = 48
V = {
 "top":   ((0.0, -0.03, 2.25), (0.0, -0.03, 1.62), 85),     # from above, back of head up in the picture
 "crown": ((0.0, 0.50, 2.00), (0.0, 0.00, 1.64), 85),       # back and above: crown and bun base
 "ear":   ((-0.38, -0.02, 1.58), (0.0, -0.02, 1.58), 85),   # left ear and side close-up
 "back":  ((0.0, 0.62, 1.58), (0.0, 0.0, 1.56), 70),        # whole back, closer than before
 "front": ((0.0, -0.62, 1.60), (0.0, 0.0, 1.58), 70),       # front, closer than before
}
for k, (loc, at, lens) in V.items():
    cam.data.lens = lens
    cam.location = Vector(loc)
    up = "Y"
    cam.rotation_euler = (Vector(at) - Vector(loc)).to_track_quat("-Z", up).to_euler()
    sc.render.filepath = f"/root/live_snaps/hi_{k}.png"
    bpy.ops.render.render(write_still=True, scene=sc.name)
print("hi-res views done")
