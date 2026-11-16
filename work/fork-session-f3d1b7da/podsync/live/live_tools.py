"""Helpers for the live pod Blender. Load with: exec(open(".../live_tools.py").read())
snap(path)            viewport picture drawn off-screen (works without the connector's screenshot)
shoot(tag)            four head views rendered with Cycles on the GPU into /root/live_snaps/<tag>_<view>.png
view_on(obj, dist)    aim the viewport straight at an object, no animation
screen_xy(point3d)    where a 3D point is on the virtual screen, for xdotool
"""
import os

import bpy
import gpu
import numpy as np
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

WIN = bpy.context.window_manager.windows[0]
AREA = next(a for a in WIN.screen.areas if a.type == "VIEW_3D")
REGION = next(r for r in AREA.regions if r.type == "WINDOW")
SPACE = AREA.spaces.active
os.makedirs("/root/live_snaps", exist_ok=True)


def ctx(obj=None):
    kw = dict(window=WIN, area=AREA, region=REGION)
    if obj is not None:
        kw.update(active_object=obj, object=obj)
    return bpy.context.temp_override(**kw)


def snap(path, w=800, h=None):
    rv3d = SPACE.region_3d
    h = h or round(w * REGION.height / REGION.width)          # same shape as the viewport, so nothing is stretched
    off = gpu.types.GPUOffScreen(w, h)
    off.draw_view3d(WIN.scene, WIN.view_layer, SPACE, REGION, rv3d.view_matrix, rv3d.window_matrix, do_color_management=True)
    with off.bind():
        buf = gpu.state.active_framebuffer_get().read_color(0, 0, w, h, 4, 0, "FLOAT")
    off.free()
    buf.dimensions = w * h * 4
    img = bpy.data.images.get("_snap") or bpy.data.images.new("_snap", w, h, alpha=True)
    if tuple(img.size) != (w, h):
        img.scale(w, h)
    img.pixels.foreach_set(np.array(buf, dtype=np.float32))
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    return path


def view_on(obj, dist=3.6, direction=(0, -1, 0)):
    rv3d = SPACE.region_3d
    rv3d.view_location = obj.location if hasattr(obj, "location") else Vector(obj)
    rv3d.view_rotation = Vector(direction).to_track_quat("Z", "Y")
    rv3d.view_distance = dist
    rv3d.view_perspective = "PERSP"


def screen_xy(p):
    c = location_3d_to_region_2d(REGION, SPACE.region_3d, Vector(p))
    return round(REGION.x + c.x), round(WIN.height - (REGION.y + c.y))


def gpu_cycles():
    cp = bpy.context.preferences.addons["cycles"].preferences
    cp.compute_device_type = "OPTIX"
    cp.get_devices()
    for d in cp.devices:
        d.use = d.type == "OPTIX"
    WIN.scene.cycles.device = "GPU"


def shoot(tag="t", w=432, h=640, samples=32, views=("hfront", "h34", "hside", "hback")):
    sc = WIN.scene
    gpu_cycles()
    body = [o for o in sc.objects if o.type == "MESH" and o.name.startswith("Mom")]
    top = max((o.matrix_world @ Vector(c)).z for o in body for c in o.bound_box)
    V = {"hfront": (0.05, -0.95, top - 0.08), "h34": (-0.62, -0.70, top - 0.08),
         "hside": (-0.88, 0.30, top - 0.06), "hback": (0.15, 0.95, top - 0.05)}
    aim = Vector((0.0, 0.0, top - 0.13))
    cam = bpy.data.objects.get("LiveCam")
    if cam is None:
        cam = bpy.data.objects.new("LiveCam", bpy.data.cameras.new("LiveCam"))
        sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = 70.0
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    sc.cycles.samples = samples
    out = []
    for v in views:
        cam.location = V[v]
        cam.rotation_euler = (aim - Vector(V[v])).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = f"/root/live_snaps/{tag}_{v}.png"
        bpy.ops.render.render(write_still=True, scene=sc.name)
        out.append(sc.render.filepath)
    return out


bpy.app.driver_namespace.update(snap=snap, shoot=shoot, view_on=view_on, screen_xy=screen_xy, ctx=ctx)
print("live tools loaded")
