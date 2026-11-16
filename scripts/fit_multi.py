"""Multi-view silhouette fit (15 Nov 2026): renders ONLY our hair (everything else is a holdout) from each reference camera and scores it against the accurate outline
(refs/outline_<view>.npy from outline_auto.py). q34 is scored above row 420 only (the outline misses the lower hair behind the ear there).
Globals from the caller: P_GAP, P_FLARE, P_CURL, P_ZEND (optional: P_GAP2), VIEWS."""
import bpy, numpy as np
exec(open("/Users/nick/Desktop/mom-character/scripts/hair2_locks.py").read())
W = bpy.context.window_manager.windows[0]; sc = W.scene
exec(open("/Users/nick/Desktop/mom-character/live/live_tools.py").read()); gpu_cycles()
hairish = lambda o: o.name.startswith(("Lock_", "Hair2_Outer", "Hair2_Fly", "Hair2_Cap"))
touched = [o for o in sc.objects if o.type in ("MESH", "CURVE", "CURVES") and not hairish(o) and not o.is_holdout]
for o in touched: o.is_holdout = True
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 520, 640, 100
sc.cycles.samples = 8; sc.render.film_transparent = True
res = {}
for v in globals().get("VIEWS", ("side", "q34")):
    sc.camera = bpy.data.objects[f"RefCam_{v}"]; sc.render.filepath = f"/root/live_snaps/fit_{v}.png"
    bpy.ops.render.render(write_still=True, scene=sc.name)
    im = bpy.data.images.load(sc.render.filepath, check_existing=False)
    alpha = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], 4)[::-1, :, 3]
    a = alpha > globals().get('ATH', 0.25)
    cov_in = float(alpha[np.load(f'/Users/nick/Desktop/mom-character/refs/outline_{v}.npy')].mean())
    print(f'  {v}: mean alpha inside her outline = {cov_in:.2f}')
    ref = np.load(f"/Users/nick/Desktop/mom-character/refs/outline_{v}.npy")
    if v == "q34": a = a.copy(); ref = ref.copy(); a[420:] = False; ref[420:] = False
    I = (a & ref).sum(); U = (a | ref).sum(); res[v] = (I / U, int((a & ~ref).sum()), int((~a & ref).sum()))
for o in touched: o.is_holdout = False
sc.render.film_transparent = False
mean = float(np.mean([r[0] for r in res.values()]))
print("FITM " + " ".join(f"{v}:IoU={r[0]:.3f}(extra {r[1]},missing {r[2]})" for v, r in res.items()) + f" MEAN={mean:.3f}")
