"""Hair from scratch, steps 5 to 7 (15 Nov 2026): bangs (+ platinum streaks), bun (twisted locks), lower half, face-framing pieces.
Same pattern as hair2_dense_top.py: guide paths from her scalp, dense children around them, built in DATA (the Comb brush and
the Interpolate modifier inputs could not be driven on the pod, see results.tsv). Every number is my plan, tuned and recorded.
Run live after hair2_dense_top.py: exec(open(".../hair2_build_rest.py").read())"""
import math
import random

import bpy
import numpy as np
from mathutils import Vector

W = bpy.context.window_manager.windows[0]
sc = W.scene
mom = sc.objects["Mom"]
PER = 14
AX = Vector((0.0, -0.06, 0.0))                     # head axis (x, y); face is -Y


def ray_face(x, z, y0=-0.30):                      # surface point seen from the front at (x, z)
    ok, loc, nrm, i = mom.ray_cast(Vector((x, y0, z)), Vector((0, 1, 0)))
    return (loc, nrm) if ok else (None, None)


def ray_polar(theta, z, r0=0.30):                  # surface point seen from outside at angle theta (0 = front, 90 = left side +X)
    d = Vector((math.sin(theta), -math.cos(theta), 0.0))
    o = Vector((AX.x, AX.y, z)) + d * r0
    ok, loc, nrm, i = mom.ray_cast(o, -d)
    return (loc, nrm, d) if ok else (None, None, d)


def resample(path, n=PER):
    path = np.asarray(path, dtype=np.float64)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    u = np.linspace(0, seg[-1], n)
    return np.stack([np.interp(u, seg, path[:, k]) for k in range(3)], axis=1)


def material(name, mel, red, rough=0.30, aspect=0.75):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    h = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
    h.parametrization = "MELANIN"
    h.model = "HUANG"
    h.inputs["Melanin"].default_value = mel
    h.inputs["Melanin Redness"].default_value = red
    h.inputs["Roughness"].default_value = rough
    h.inputs["Aspect Ratio"].default_value = aspect
    nt.links.new(h.outputs[0], o.inputs["Surface"])
    return mat


def build(name, C, mat, radius=0.00011):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    C = np.asarray(C)
    N, per = C.shape[0], C.shape[1]
    cd = bpy.data.hair_curves.new(name)
    cd.add_curves([per] * N)
    cd.attributes["position"].data.foreach_set("vector", C.reshape(-1).astype(np.float32))
    rad = cd.attributes.get("radius") or cd.attributes.new("radius", "FLOAT", "POINT")
    rad.data.foreach_set("value", np.full(N * per, radius, dtype=np.float32))
    cd.surface = mom
    cd.surface_uv_map = "UVMap"
    ob = bpy.data.objects.new(name, cd)
    sc.collection.objects.link(ob)
    ob.parent = mom
    cd.materials.append(mat)
    print(f"{name}: {N} curves x {per} points")
    return ob


def children(guides, n_per, spread, clump=0.45, frizz=0.0006, snap=True, keep=lambda s: True, seed=3):
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, guides[0].shape[0])[:, None]
    out = []
    for g in guides:
        made = tries = 0
        while made < n_per and tries < n_per * 8:
            tries += 1
            off = np.array([rng.gauss(0, spread), rng.gauss(0, spread), rng.gauss(0, spread)])
            if snap:
                ok, loc, nrm, i = mom.closest_point_on_mesh(Vector(g[0] + off))
                S = np.array(loc)
                if not keep(S):
                    continue
                off = S - g[0]
            child = g + off[None, :] * (1.0 - clump * t) + np_rng.normal(0, frizz, g.shape) * t
            out.append(child); made += 1
    return np.array(out)


# ---------------- bangs: curtain, centre part, to the cheekbones (reference 64.5 s, 55.5 s) ----------------
bangs, streaks = [], []
for side in (-1, 1):
    for k in range(14):
        xr = side * (0.014 + 0.0075 * k)                       # roots along the hairline, from the part outward
        pts = []
        for s in np.linspace(0, 1, 9):
            x = xr + side * 0.050 * s ** 1.3                    # sweep outward as it falls
            z = 1.628 - 0.085 * s
            loc, nrm = ray_face(x, z)
            if loc is None:
                break
            pts.append(np.array(loc + nrm * (0.007 + 0.006 * s)))
        if len(pts) == 9:
            g = resample(pts)
            (streaks if (abs(xr) % 0.03 > 0.017 and abs(xr) % 0.03 < 0.024) else bangs).append(g)
print("bang guides", len(bangs), "streak guides", len(streaks))
mat_bang = material("Hair2_Bangs", 0.42, 0.55)
mat_streak = material("Hair2_Streaks", 0.16, 0.3)
build("Hair2_Bangs", children(bangs, 150, 0.004, clump=0.2, snap=False), mat_bang)
build("Hair2_Streaks", children(streaks, 90, 0.003, clump=0.2, snap=False), mat_streak)

# ---------------- bun: a few twisted locks in a spiral, dark, high at the back of the crown (62.0 s, 35.0 s) ----------------
C0 = np.array([0.0, 0.050, 1.628])
locks = []
for j in range(6):
    ph = j * 2 * math.pi / 6
    xo = (j - 2.5) * 0.005
    pts = []
    for s in np.linspace(0, 1, 40):
        ang = ph + 2 * math.pi * 1.6 * s
        R = 0.024 * (1 - 0.70 * s)
        pts.append([xo * (1 - 0.5 * s), C0[1] + R * math.cos(ang), C0[2] + R * math.sin(ang)])
    locks.append(resample(pts, 20))
mat_bun = material("Hair2_Bun", 0.80, 0.55, rough=0.35)
build("Hair2_Bun", children(locks, 600, 0.0030, clump=0.1, snap=False, frizz=0.0004), mat_bun, radius=0.00012)

# ---------------- lower half: straight to the collar, ends turned under; pieces in front of the ears, ends flick out ----------------
low = []
for side in (-1, 1):
    for th in np.radians(np.arange(56, 181, 4.5)):
        for z in (1.535, 1.57, 1.592):
            ang = side * th
            ear = 66 <= math.degrees(th) <= 122
            if ear and z < 1.585:                                     # her ear stays free
                continue
            loc, nrm, d = ray_polar(ang, z)
            if loc is None or loc.z > 1.62:
                continue
            R = np.array(loc)
            z_end = 1.455 - 0.022 * math.cos(3 * th) - 0.018 * math.sin(11 * th + z * 40)
            pts = []
            for s in np.linspace(0, 1, 12):
                out = 0.010 + 0.010 * s - 0.024 * max(0.0, (s - 0.78) / 0.22)       # ends drawn in
                zz = R[2] + (z_end - R[2]) * s
                p = np.array([R[0], R[1] + (0.05 * s if ear else 0.0), zz]) + np.array([d.x, d.y, 0.0]) * out
                pts.append(p)
            low.append(resample(pts))
print("lower guides", len(low))
mat_low = material("Hair2_Lower", 0.52, 0.58)
build("Hair2_Lower", children(low, 130, 0.010, clump=0.35, snap=True, keep=lambda S: S[2] < 1.62 and S[2] > 1.50), mat_low)

pieces = []
for side in (-1, 1):
    for th in np.radians((60, 64, 68)):
        loc, nrm, d = ray_polar(side * th, 1.592)
        if loc is None:
            continue
        R = np.array(loc)
        pts = []
        for s in np.linspace(0, 1, 10):
            out = 0.009 + 0.004 * s + 0.020 * max(0.0, (s - 0.7) / 0.3)             # ends flick out
            p = np.array([R[0], R[1] - 0.012 * s, R[2] + (1.472 - R[2]) * s]) + np.array([d.x, d.y, 0.0]) * out
            pts.append(p)
        pieces.append(resample(pts))
mat_piece = material("Hair2_Pieces", 0.45, 0.55)
build("Hair2_Pieces", children(pieces, 110, 0.006, clump=0.3, snap=False), mat_piece)
print("rest built")
