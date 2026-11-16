"""Cursor sculpting (15 Nov 2026). Research (memory blender-live-on-pod): enter the mode in ONE call, stroke in the NEXT, read results only AFTER leaving the mode.
This script: selects a strand layer, enters Curves Sculpt, activates Comb, switches the viewport to the reference camera, and returns screen strokes that push the
strands that stick OUT of her silhouette (the red area) back inside it. Globals: LAYER (object name), NSTROKES."""
import bpy, json, numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
W = bpy.context.window_manager.windows[0]; sc = W.scene
A = next(a for a in W.screen.areas if a.type == "VIEW_3D"); R = next(r for r in A.regions if r.type == "WINDOW"); SP = A.spaces.active
cam = bpy.data.objects["RefCam_side"]; sc.camera = cam; SP.region_3d.view_perspective = "CAMERA"; SP.shading.type = "SOLID"
for ar in W.screen.areas: ar.tag_redraw()
POLY = np.array([(30,190),(55,150),(110,125),(200,112),(300,125),(345,160),(383,230),(378,285),(335,300),(285,305),(268,340),(255,400),(235,480),(195,530),(130,553),(105,500),(75,380),(65,300),(35,250)], np.float32)
def poly_info(pts, P):
    """for each point: signed distance to the polygon (positive outside) and the outward unit vector"""
    A = P; B = np.roll(P, -1, axis=0); AB = B - A; L2 = (AB ** 2).sum(1)
    t = np.clip(((pts[:, None, :] - A[None]) * AB[None]).sum(2) / L2[None], 0, 1)
    C = A[None] + t[..., None] * AB[None]; d = np.linalg.norm(pts[:, None, :] - C, axis=2); j = d.argmin(1)
    near = C[np.arange(len(pts)), j]; dist = d[np.arange(len(pts)), j]
    inside = np.zeros(len(pts), bool)
    for i in range(len(P)):
        x1, y1 = P[i]; x2, y2 = P[(i + 1) % len(P)]
        c = ((y1 > pts[:, 1]) != (y2 > pts[:, 1])) & (pts[:, 0] < (x2 - x1) * (pts[:, 1] - y1) / (y2 - y1 + 1e-9) + x1); inside ^= c
    sd = np.where(inside, -dist, dist); v = pts - near; v /= (np.linalg.norm(v, axis=1, keepdims=True) + 1e-9)
    v = np.where(inside[:, None], -v, v)
    return sd, v
ob = bpy.data.objects[globals().get("LAYER", "Hair2_Outer_Low")]
n = len(ob.data.points); P = np.zeros(n * 3, np.float32); ob.data.attributes["position"].data.foreach_get("vector", P); P = P.reshape(-1, 3)
M = np.array(ob.matrix_world)
Pw = (M[:3, :3] @ P.T).T + M[:3, 3]
f_px = cam.data.lens / 36.0 * 520
uv = np.array([world_to_camera_view(sc, cam, Vector(p))[:2] for p in Pw[::7]])        # sample every 7th point
px = np.stack([uv[:, 0] * 520, (1 - uv[:, 1]) * 640], 1)
sd, outv = poly_info(px.astype(np.float32), POLY)
out = np.maximum(sd, 0); sel = np.where((sd > 4) & (px[:, 0] > 0) & (px[:, 0] < 520))[0]
print("sampled", len(uv), "outside silhouette:", len(sel))
# cluster by 40 px grid, keep the cells with most outside points
cells = {}
for k in sel:
    cells.setdefault((int(px[k, 0] // 40), int(px[k, 1] // 40)), []).append(k)
top = sorted(cells.items(), key=lambda kv: -len(kv[1]))[: globals().get("NSTROKES", 6)]
Rt = np.array(cam.matrix_world.to_3x3()); camx = Rt[:, 0]; camy = Rt[:, 1]; camz = Rt[:, 2]
cpos = np.array(cam.matrix_world.translation)
from bpy_extras.view3d_utils import location_3d_to_region_2d
strokes = []
for (cx, cy), ks in top:
    kk = np.array(ks); mid = px[kk].mean(0); idx = kk[len(kk) // 2]
    g = outv[kk].mean(0); g = g / (np.linalg.norm(g) + 1e-9)                                       # outward direction (image px)
    need = float(out[idx]) + 6.0                                                                     # px to move inward
    p3 = Pw[idx * 7]; depth = float(np.dot(p3 - cpos, -camz))
    shift = need * depth / f_px                                                                      # metres
    d3 = -(g[0] * camx - g[1] * camy) * shift                                                       # image y is down, camera y is up
    a = location_3d_to_region_2d(R, SP.region_3d, Vector(p3)); b = location_3d_to_region_2d(R, SP.region_3d, Vector(p3 + d3))
    if a is None or b is None: continue
    sx, sy = R.x + a.x, W.height - (R.y + a.y); ex, ey = R.x + b.x, W.height - (R.y + b.y)
    strokes.append([[round(sx), round(sy)], [round(ex), round(ey)], int(len(ks)), round(need, 1)])
bpy.app.driver_namespace["comb_before"] = P.copy()
with bpy.context.temp_override(window=W, area=A, region=R, active_object=ob, object=ob):
    for o in sc.objects: o.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="SCULPT_CURVES")
    bpy.ops.brush.asset_activate(asset_library_type='ESSENTIALS', relative_asset_identifier='brushes/essentials_brushes-curve_sculpt.blend/Brush/Comb')
cs = bpy.context.tool_settings.curves_sculpt; cs.brush.size = 90; cs.unified_paint_settings.size = 90; cs.brush.falloff_shape = "PROJECTED"
print("mode", ob.mode, "brush", cs.brush.name, "layer", ob.name, "points", n)
print("STROKES", json.dumps(strokes))
