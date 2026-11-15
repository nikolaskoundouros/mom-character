"""The mom from "My Mom Cracked The Dinosaur", built like the boy (blender-funnel run 013), as a probe.

Reference read from the clip (frames 4.3 to 71.4 s): a woman about 40 to 45, slim and curvy, light
tan skin; honey-blonde hair pulled back into a bun, with long bangs and loose strands at the face;
a fitted white polo (pointed collar, a short zip placket, a small red and gold crest on her left
chest, short sleeves with a thin rib); cream slim trousers; white trainers.
Assets (MakeHuman CC0): female_casualsuit01 (tee recoloured white, jeans recoloured cream),
ponytail01 (recoloured), shoes05 (white trainers), middleage_caucasian_female skin.
The crest is an original look-alike (red oval, gold rim, gold crown), not the clip's logo.

Usage: blender python mom.py [width height samples]
Environment: SLIDERS (json), VIEWS (comma list), OUT, HAIR_RGB, TOP_RGB, PANTS_RGB, SPLIT (top/trousers
height above the hip joint, metres), COLLAR (1 = add the polo collar band), CREST (1 = add the crest).
"""
import json
import math
import os
import sys
import time

import bpy
import numpy as np

sys.path.insert(0, "/Users/nick/Desktop/blender-funnel")
from recipes import accessories, camera, color, human, lighting, looks, materials, prints, render, sculpt, stage, world  # noqa: E402
from recipes import rig as _rig  # noqa: E402
from mathutils import Vector  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, SAMPLES = (int(a) for a in sys.argv[1:4]) if len(sys.argv) > 3 else (432, 640, 24)
env = lambda k, d: type(d)(os.environ.get(k, d))
rgb = lambda k, d: tuple(float(v) for v in os.environ.get(k, d).split(","))
t0 = time.time()

S = dict(gender=0.0, age=0.70, muscle=0.45, weight=0.50, height=0.55, proportions=0.6, cupsize=0.75, firmness=0.6,
         caucasian=1, african=0, asian=0)
S.update(json.loads(os.environ.get("SLIDERS", "{}")))
HAIR = rgb("HAIR_RGB", "0.95,0.58,0.22")          # honey blonde (linear)
TOP = rgb("TOP_RGB", "0.82,0.80,0.74")            # white polo, a touch warm
PANTS = rgb("PANTS_RGB", "0.66,0.60,0.50")        # cream trousers

scene = stage.new_scene()
base_verts = human.morphed_base(**S)
ARM = env("ARM", 0.18)
pose = looks.head_pose(6.0, -3.0, 8.0) + _rig._arm("L", (ARM, 0.0, -1.0), (ARM * 0.5, -0.2, -1.0)) \
    + _rig._arm("R", (ARM, 0.0, -1.0), (ARM * 0.5, -0.2, -1.0))
mom = human.build_human(scene, name="Mom", skin=os.environ.get("SKIN", "middleage_caucasian_female"), hair=None if os.environ.get("HAIR", "scratch") == "scratch" else "ponytail01",
                        eyes="brown", eyebrows=os.environ.get("BROWS", "eyebrow002"),
                        outfit=("female_casualsuit01", "shoes05"), pose=pose, **S)
kids = list(mom.children_recursive)
by = {o.name: o for o in kids}
print("objects:", sorted(by), flush=True)
body = looks.body_of(mom, "Mom")
marks = sculpt.landmarks(human.to_blender(base_verts))


def bsdf_of(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def drop_base_links(mat):
    b = bsdf_of(mat)
    for l in [l for l in mat.node_tree.links if l.to_socket == b.inputs["Base Color"]]:
        mat.node_tree.links.remove(l)
    return b


# ---- outfit: white top above the waist, cream trousers below, keep the modelled fold texture
suit = by["Mom_female_casualsuit01"]
smat = suit.data.materials[0]
nodes, links = smat.node_tree.nodes, smat.node_tree.links
b = drop_base_links(smat)
geo = nodes.new("ShaderNodeNewGeometry")
sep = nodes.new("ShaderNodeSeparateXYZ"); links.new(geo.outputs["Position"], sep.inputs[0])
split_z = float(marks["hips"][2]) + env("SPLIT", 0.07)
above = nodes.new("ShaderNodeMath"); above.operation = "GREATER_THAN"
links.new(sep.outputs["Z"], above.inputs[0]); above.inputs[1].default_value = split_z
mix = nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
links.new(above.outputs[0], mix.inputs["Factor"])
mix.inputs["A"].default_value = PANTS + (1.0,)
mix.inputs["B"].default_value = TOP + (1.0,)
links.new(mix.outputs["Result"], b.inputs["Base Color"])
b.inputs["Roughness"].default_value = 0.8
for nm in [n for n in nodes if n.type == "NORMAL_MAP"]:
    nm.inputs["Strength"].default_value = env("FOLDS", 0.6)
print(f"top / trousers split at z {split_z:.3f}", flush=True)

# ---- hair: honey blonde, keeping the strand texture's light and dark (only with the old ponytail asset, HAIR=asset)
hair = by.get("Mom_ponytail01")
hmat = hair.data.materials[0] if hair else None
if hmat:
    hn, hl = hmat.node_tree.nodes, hmat.node_tree.links
    hb = bsdf_of(hmat)
    src = next((l.from_socket for l in hl if l.to_socket == hb.inputs["Base Color"]), None)
if hmat and src is not None:
    for l in [l for l in hl if l.to_socket == hb.inputs["Base Color"]]:
        hl.remove(l)
    bw = hn.new("ShaderNodeRGBToBW"); hl.new(src, bw.inputs[0])
    gain = hn.new("ShaderNodeMath"); gain.operation = "MULTIPLY"; gain.inputs[1].default_value = env("HAIR_GAIN", 3.2)
    hl.new(bw.outputs[0], gain.inputs[0])
    tint = hn.new("ShaderNodeMix"); tint.data_type = "RGBA"; tint.blend_type = "MULTIPLY"; tint.inputs["Factor"].default_value = 1.0
    hl.new(gain.outputs[0], tint.inputs["A"]); tint.inputs["B"].default_value = HAIR + (1.0,)
    hl.new(tint.outputs["Result"], hb.inputs["Base Color"])
if hmat:
    hb.inputs["Roughness"].default_value = 0.55


# ---- crest on her left chest (original look-alike)
def crest(x, y):
    soft = lambda d, w=0.03: np.clip(0.5 - d / w, 0.0, 1.0)
    srgb = prints._srgb
    rgbv = np.zeros(x.shape + (3,)); alpha = np.zeros(x.shape)
    oval = (x / 0.55) ** 2 + ((y + 0.12) / 0.5) ** 2
    rim = soft(np.sqrt(oval) - 1.0, 0.05)
    a = rim; rgbv += a[..., None] * srgb((0.80, 0.50, 0.02)); alpha = np.maximum(alpha, a)
    inner = soft(np.sqrt(oval) - 0.82, 0.05)
    rgbv = rgbv * (1 - inner[..., None]) + inner[..., None] * srgb((0.62, 0.0, 0.0)); alpha = np.maximum(alpha, inner)
    crown = soft(y - 0.62, 0.03) * soft(-(y - 0.38), 0.03) * soft(np.abs(x) - 0.30, 0.03)
    for cx in (-0.22, 0.0, 0.22):                       # three crown points
        crown = np.maximum(crown, soft(np.hypot(x - cx, y - 0.66) - 0.07, 0.03))
    rgbv = rgbv * (1 - crown[..., None]) + crown[..., None] * srgb((0.85, 0.58, 0.04)); alpha = np.maximum(alpha, crown)
    rgbv = rgbv / np.maximum(alpha, 1e-4)[..., None]
    return np.clip(rgbv, 0, 1), alpha


if env("CREST", 1):
    tco = [v.co for v in suit.data.vertices]
    want = Vector((0.075, 0.0, float(marks["chest"][2]) + env("CREST_UP", 0.11)))
    cands = [c for c in tco if abs(c.x - want.x) < 0.012 and abs(c.z - want.z) < 0.012]
    centre = min(cands, key=lambda c: c.y) if cands else min(tco, key=lambda c: (c - want).length)
    uv0, inv, fit_err, used = prints.fit_uv_frame(suit, np.array(centre), radius=0.06)
    prints.apply(smat, prints.graphic_image(crest, name="Crest", aspect=1.0), uv0, inv, width=env("CREST_W", 0.10), aspect=1.0)
    print(f"crest fit error {fit_err:.4f} on {used} points", flush=True)

# ---- skin: warm tan
bmat = body.data.materials[0]
bn, bl = bmat.node_tree.nodes, bmat.node_tree.links
bb = bsdf_of(bmat)
bsrc = next((l.from_socket for l in bl if l.to_socket == bb.inputs["Base Color"]), None)
if bsrc is not None:
    for l in [l for l in bl if l.to_socket == bb.inputs["Base Color"]]:
        bl.remove(l)
    tan = bn.new("ShaderNodeMix"); tan.data_type = "RGBA"; tan.blend_type = "MULTIPLY"; tan.inputs["Factor"].default_value = 1.0
    bl.new(bsrc, tan.inputs["A"]); tan.inputs["B"].default_value = rgb("TAN_RGB", "0.93,0.63,0.41") + (1.0,)
    bl.new(tan.outputs["Result"], bb.inputs["Base Color"])


# ---- polo collar and placket, built on the shirt's neckline as posed
def boundary_loops(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg); me = ev.to_mesh(); mw = ev.matrix_world
    co = [mw @ v.co for v in me.vertices]
    count = {}
    for p in me.polygons:
        for ek in p.edge_keys:
            count[ek] = count.get(ek, 0) + 1
    adj = {}
    for (a, b2), c in count.items():
        if c == 1:
            adj.setdefault(a, []).append(b2); adj.setdefault(b2, []).append(a)
    ev.to_mesh_clear()
    loops, seen = [], set()
    for st in adj:
        if st in seen:
            continue
        loop, prev, cur = [st], None, st
        seen.add(st)
        while True:
            nxt = [x for x in adj[cur] if x != prev and x not in seen]
            if not nxt:
                break
            prev, cur = cur, nxt[0]; seen.add(cur); loop.append(cur)
        if len(loop) >= 8:
            loops.append([co[k].copy() for k in loop])
    return loops


if env("COLLAR", 1):
    import bmesh
    # the shirt's own neckline (a wide crew neck) and the base of her neck
    loops = [L for L in boundary_loops(suit) if abs(sum(p.x for p in L) / len(L)) < 0.08]
    neck = max(loops, key=lambda L: sum(p.z for p in L) / len(L))
    npts = np.array([[p.x, p.y, p.z] for p in neck])
    for _ in range(10):
        npts = 0.5 * npts + 0.25 * (np.roll(npts, 1, 0) + np.roll(npts, -1, 0))
    dg = bpy.context.evaluated_depsgraph_get()
    bev = body.evaluated_get(dg); bme = bev.to_mesh(); bmw = bev.matrix_world
    bco = np.array([list(bmw @ v.co) for v in bme.vertices]); bev.to_mesh_clear()
    z_base = float(np.median(npts[:, 2])) + env("NECK_UP", 0.022)   # collar base: a little above the neckline's middle height
    ring = bco[(np.abs(bco[:, 2] - z_base) < 0.008) & (np.abs(bco[:, 0]) < 0.09)]
    cx, cy = float(np.median(ring[:, 0])), float((ring[:, 1].min() + ring[:, 1].max()) / 2)
    angf = lambda P: np.arctan2(P[:, 0] - cx, -(P[:, 1] - cy))        # 0 = front centre
    ra = angf(ring); rr = np.hypot(ring[:, 0] - cx, ring[:, 1] - cy)
    na = angf(npts); order = np.argsort(na); na, npts = na[order], npts[order]
    A = np.linspace(-np.pi, np.pi, 97)[:-1]
    def neck_r(a):
        d = np.abs((ra - a + np.pi) % (2 * np.pi) - np.pi)
        return float(rr[d < 0.25].max()) if (d < 0.25).any() else float(rr.max())
    clear = env("NECK_CLEAR", 0.008)
    near = bco[(bco[:, 2] > z_base - 0.20) & (bco[:, 2] < z_base + 0.03) & (np.hypot(bco[:, 0] - cx, bco[:, 1] - cy) < 0.20)]
    near_a, near_r = angf(near), np.hypot(near[:, 0] - cx, near[:, 1] - cy)
    def outside(v):
        a = np.arctan2(v[0] - cx, -(v[1] - cy)); r = np.hypot(v[0] - cx, v[1] - cy)
        m = (np.abs((near_a - a + np.pi) % (2 * np.pi) - np.pi) < 0.12) & (np.abs(near[:, 2] - v[2]) < 0.008)
        if not m.any():
            return v
        rb = float(near_r[m].max()) + 0.006
        if r >= rb:
            return v
        return np.array([cx + rb * np.sin(a), cy - rb * np.cos(a), v[2]])
    inner = np.array([[cx + (neck_r(a) + clear) * np.sin(a), cy - (neck_r(a) + clear) * np.cos(a), z_base] for a in A])
    outer = np.array([[np.interp(a, na, npts[:, k], period=2 * np.pi) for k in range(3)] for a in A])
    gap_top, gap_low = env("V_TOP", 0.30), env("V_LOW", 0.18)          # front opening, radians, at the neck and at the neckline
    stand, fall = env("COLLAR_STAND", 0.020), env("COLLAR_FALL", 0.034)
    bm = bmesh.new()
    # 1. yoke: shirt fabric from the old neckline up to the neck, open at the front in a V
    rows = []
    for a, po, pi in zip(A, outer, inner):
        if abs(a) < gap_low:
            rows.append(None); continue
        t = np.clip((abs(a) - gap_low) / max(gap_top - gap_low, 1e-3), 0, 1)
        top = pi if abs(a) >= gap_top else po + (pi - po) * t * 0.98
        rows.append([bm.verts.new(tuple(outside(po + (top - po) * f))) for f in (0.0, 0.25, 0.5, 0.75, 1.0)])
    for k in range(len(A)):
        r0, r1 = rows[k], rows[(k + 1) % len(A)]
        if r0 is None or r1 is None:
            continue
        for j in range(4):
            bm.faces.new((r0[j], r1[j], r1[j + 1], r0[j + 1]))
    # 2. collar: stands up round the neck, then folds out and down; pointed tips at the front
    crow = []
    for a, pi in zip(A, inner):
        if abs(a) < gap_top:
            crow.append(None); continue
        out = np.array([np.sin(a), -np.cos(a), 0.0])
        tip = 1.0 + env("TIP", 0.8) * max(0.0, 1.0 - (abs(a) - gap_top) / 0.55)
        c0 = pi
        c1 = pi + np.array([0, 0, stand]) + 0.002 * out
        c2 = c1 + 0.006 * out + np.array([0, 0, 0.002])
        c3 = c2 + fall * tip * (0.38 * out + np.array([0, 0, -0.92]))
        crow.append([bm.verts.new(tuple(v)) for v in (c0, c1, c2, c3)])
    for k in range(len(A)):
        r0, r1 = crow[k], crow[(k + 1) % len(A)]
        if r0 is None or r1 is None:
            continue
        for j in range(3):
            bm.faces.new((r0[j], r1[j], r1[j + 1], r0[j + 1]))
    cm = bpy.data.meshes.new("Collar"); bm.to_mesh(cm); bm.free()
    for poly in cm.polygons:
        poly.use_smooth = True
    collar = bpy.data.objects.new("Collar", cm); scene.collection.objects.link(collar)
    cm.materials.append(materials.plain("PoloWhite", TOP, 0.8))
    sol = collar.modifiers.new("Thickness", "SOLIDIFY"); sol.thickness = 0.0025
    sub = collar.modifiers.new("Smooth", "SUBSURF"); sub.levels = sub.render_levels = 2
    # placket: two seam lines down from the V, and a small zip pull
    for side in (-1, 1):
        a = side * gap_low
        q = np.array([np.interp(a, na, npts[:, k], period=2 * np.pi) for k in range(3)])
        top_pt = inner[np.argmin(np.abs(A - side * gap_top))]
        cu = bpy.data.curves.new(f"Placket{side}", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.0014
        sp = cu.splines.new("POLY"); sp.points.add(2)
        for k, v in enumerate((top_pt, q, q + np.array([0, 0.004, -env("PLACKET", 0.06)]))):
            sp.points[k].co = (float(v[0]), float(v[1]) - 0.002, float(v[2]), 1.0)
        ob = bpy.data.objects.new(f"Placket{side}", cu); scene.collection.objects.link(ob)
        ob.data.materials.append(materials.plain("Seam", tuple(v * 0.55 for v in TOP), 0.8))
    print(f"collar round the neck at z {z_base:.3f}, neck radius {np.median([neck_r(a) for a in A]):.3f}, V {gap_top}/{gap_low} rad", flush=True)

# ---- bangs: a centre-parted fringe falling to the cheekbones, grown as strands (repo haircut tool)
if env("BANGS", 0 if os.environ.get("HAIR", "scratch") == "scratch" else 1):
    from recipes import haircut

    def fringe(scalp, points):
        h = points[:, 2] - scalp.eye_z
        back = points[:, 1] - scalp.lm["front_y"]
        x = np.abs(points[:, 0])
        w_front = haircut._sigmoid(env("BANG_DEPTH", 0.075) - back, 0.008)
        density = haircut._sigmoid(x - 0.016, 0.003) * w_front * haircut._sigmoid(h - 0.035, 0.004) * haircut._sigmoid(0.115 - h, 0.006) * haircut._sigmoid(0.075 - x, 0.006)
        length = env("BANG_LEN", 0.075) * (0.6 + 0.8 * np.clip(x / 0.06, 0, 1))
        comb = np.stack([np.sign(points[:, 0]) * env("BANG_SPREAD", 2.2), -0.25 * np.ones(len(points)), -np.ones(len(points))], axis=1)
        comb /= np.linalg.norm(comb, axis=1, keepdims=True)
        return density, np.full(len(points), 1.0) * length, comb, np.zeros(len(points))

    hm = haircut.material("Bangs", melanin=0.3, white=0.0, redness=0.5, roughness=0.4)
    hp = next(n for n in hm.node_tree.nodes if n.type == "BSDF_HAIR_PRINCIPLED")
    hp.parametrization = "COLOR"
    hp.inputs["Color"].default_value = rgb("BANG_RGB", "0.36,0.13,0.025") + (1.0,)
    scalp = haircut.Scalp(base_verts)
    g_roots, _ = haircut.sample_roots(scalp, 300, fringe, seed=3, oversample=40)
    guides = haircut.grow_guides(scalp, g_roots, fringe, steps=12, lift=(env("BANG_LIFT0", 0.004), env("BANG_LIFT1", 0.016)), seed=3)
    c_roots, _ = haircut.sample_roots(scalp, env("BANG_N", 30000), fringe, seed=4, oversample=40)
    kids = haircut.interpolate(scalp, guides, c_roots, clump=0.6, frizz=0.0012, seed=5)
    bobj = haircut.build(scene, "Bangs", kids, np.zeros(len(kids)), hm, radius=0.00006)
    binfo = {"guides": len(guides), "children": len(kids)}
    _rig.parent_to_bone(bobj, mom, "head")
    scene.cycles_curves.shape = "THICK"
    print("bangs:", binfo, flush=True)

# ---- hair from scratch: the half-up bun (mom_hair.py)
if os.environ.get("HAIR", "scratch") == "scratch":
    sys.path.insert(0, HERE)
    import mom_hair  # noqa: E402
    mom_hair.half_up_bun(scene, base_verts, mom)

# ---- scene, light and cameras as for the boy
world.sky_world(scene, sun_elevation_deg=40.0, sun_rotation_deg=220.0, strength=0.006)
if os.environ.get("ROOM"):                       # warm indoor light like the reference museum, instead of the blue sky
    _w = scene.world.node_tree
    _bg = next(n for n in _w.nodes if n.type == "BACKGROUND")
    for _l in list(_bg.inputs["Color"].links):
        _w.links.remove(_l)
    _bg.inputs["Color"].default_value = rgb("ROOM_RGB", "0.30,0.19,0.11") + (1.0,)
    _bg.inputs["Strength"].default_value = float(os.environ["ROOM"])
target = stage.empty_at(scene, "Body", (0.0, 0.0, 0.9))
lighting.three_point(scene, target, (-0.6, -3.5, 1.2), key_power=env("KEY", 260.0), fill_ratio=0.35, rim_ratio=1.2,
                     distance=3.5, key_size=1.8)
bpy.ops.mesh.primitive_plane_add(size=40)
bpy.context.object.data.materials.append(materials.plain("Carpet", (0.12, 0.025, 0.025), 0.95))
color.set_view(scene, "AgX", look="Medium High Contrast")
render.cycles_cpu(scene, width=W, height=H, samples=SAMPLES)
if os.environ.get("NO_RENDER"):                  # live session: build the scene, leave rendering to the viewport
    raise SystemExit(0)
top = accessories.face_landmarks(base_verts)["top_z"]
views = {"full": ((-0.9, -3.4, 1.05), (0.0, 0.0, top * 0.52), 50.0),
         "upper": ((-0.45, -1.7, top * 0.82), (0.0, 0.0, top * 0.76), 60.0),
         "close": ((-0.25, -1.0, top * 0.90), (0.0, 0.0, top * 0.86), 60.0),
         "side": ((-3.4, -0.4, 1.05), (0.0, 0.0, top * 0.52), 50.0),
         "back": ((0.7, 3.4, 1.15), (0.0, 0.0, top * 0.52), 50.0),
         "hfront": ((0.05, -0.95, top - 0.08), (0.0, 0.0, top - 0.13), 70.0),
         "h34": ((-0.62, -0.70, top - 0.08), (0.0, 0.0, top - 0.13), 70.0),
         "hside": ((-0.88, 0.30, top - 0.06), (0.0, 0.0, top - 0.13), 70.0),
         "hback": ((0.15, 0.95, top - 0.05), (0.0, 0.0, top - 0.13), 70.0)}
names = os.environ.get("VIEWS", "full,upper,close").split(",")
from PIL import Image  # noqa: E402
tiles = []
for label in names:
    for o in [o for o in scene.objects if o.type == "CAMERA"]:
        bpy.data.objects.remove(o, do_unlink=True)
    eye, at, lens = views[label]
    camera.camera_at(scene, eye, stage.empty_at(scene, f"Aim_{label}", at), lens=lens)
    path = os.path.join(HERE, f"mom_{label}.png")
    render.render_to(scene, path)
    tiles.append(Image.open(path).convert("RGB"))
sheet = Image.new("RGB", (W * len(tiles), H))
for i, t in enumerate(tiles):
    sheet.paste(t, (W * i, 0))
sheet.save(os.environ.get("OUT") or os.path.join(HERE, "mom.png"))
print(f"STATS height {top:.3f} m, sliders {S}, {time.time() - t0:.0f} s", flush=True)
