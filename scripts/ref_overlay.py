"""Reference-in-Blender (15 Nov 2026). One camera per reference frame (refs/cams.json: pose from cv2.solvePnP on face/ear landmarks, back = side camera orbited 19.7 deg)
with the reference frame as the camera background image. In the live Blender: View > Cameras > RefCam_<name>. Run live: exec(open(".../ref_overlay.py").read())
RENDER=True also renders each view with a transparent background to /root/live_snaps/rc_<name>.png for the overlay sheet."""
import bpy, json
from mathutils import Matrix, Vector
W = bpy.context.window_manager.windows[0]; sc = W.scene
L = "/Users/nick/Desktop/mom-character"
J = json.load(open(f"{L}/refs/cams.json"))
for name, c in J.items():
    cn = f"RefCam_{name}"
    cam = bpy.data.objects.get(cn)
    if cam is None:
        cam = bpy.data.objects.new(cn, bpy.data.cameras.new(cn)); sc.collection.objects.link(cam)
    cam.data.sensor_fit = "HORIZONTAL"; cam.data.sensor_width = 36.0; cam.data.lens = c["f_mm"]
    cam.matrix_world = Matrix.Translation(Vector(c["loc"])) @ Matrix(c["rot"]).to_4x4()
    cam.data.show_background_images = True
    for b in list(cam.data.background_images):
        cam.data.background_images.remove(b)
    bg = cam.data.background_images.new(); bg.image = bpy.data.images.load(f"{L}/refs/heads/{c['img']}", check_existing=True)
    bg.alpha = 0.55; bg.display_depth = "BACK"; bg.frame_method = "FIT"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 520, 640, 100
A = next(a for a in W.screen.areas if a.type == "VIEW_3D"); sp = A.spaces.active
sc.camera = bpy.data.objects["RefCam_side"]; sp.region_3d.view_perspective = "CAMERA"; sp.shading.type = "RENDERED"
if globals().get("RENDER"):
    exec(open(f"{L}/live/live_tools.py").read()); gpu_cycles(); sc.cycles.samples = 48; sc.render.film_transparent = True
    for name in J:
        sc.camera = bpy.data.objects[f"RefCam_{name}"]; sc.render.filepath = f"/root/live_snaps/rc_{name}.png"
        bpy.ops.render.render(write_still=True, scene=sc.name)
    sc.render.film_transparent = False; sc.camera = bpy.data.objects["RefCam_side"]
for ar in W.screen.areas: ar.tag_redraw()
print("ref cameras:", list(J))
