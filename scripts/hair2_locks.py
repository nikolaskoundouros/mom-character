"""Hair from scratch, the tutorial's LOCKS method (15 Nov 2026), in Blender 5.2.2.
Source: the video "Blender Tutorial - Hair With Curves" (2.79; two frames re-checked 15 Nov: 2:36 and 18:01): one Path curve per lock,
a shared Bezier-circle-like bevel (flat, grooved), width per point (radius) and tilt (twist) per point, shading with noise along the lock.
Here every lock is built from a computed path (the pod's mouse could not drive brushes); numbers are my plan, tuned and recorded in results.tsv.
Run live: exec(open(".../hair2_locks.py").read())"""
import math
import random

import bpy
import numpy as np
from mathutils import Vector

W = bpy.context.window_manager.windows[0]
sc = W.scene
mom = sc.objects["Mom"]
AX = Vector((0.0, -0.06, 0.0))
BUN = Vector((0.0, 0.030, 1.640))
inv = mom.matrix_world.inverted()
rng = random.Random(11)

# --- clean up earlier hair2 objects and hide the strand clouds (kept for flyaways later)
for o in list(sc.objects):
    if o.name.startswith("Lock_") or o.name == "Hair2_Profile":
        bpy.data.objects.remove(o, do_unlink=True)
for n in ("Hair_Top", "Hair_Top_dense", "Hair2_Bangs", "Hair2_Streaks", "Hair2_Bun", "Hair2_Lower", "Hair2_Pieces"):
    if n in sc.objects:
        sc.objects[n].hide_render = True
        sc.objects[n].hide_viewport = True


def ray_down(x, y):
    ok, loc, nrm, i = mom.ray_cast(inv @ Vector((x, y, 1.9)), inv.to_3x3() @ Vector((0, 0, -1)))
    return (mom.matrix_world @ loc) if ok else None


def ray_face(x, z):
    ok, loc, nrm, i = mom.ray_cast(Vector((x, -0.30, z)), Vector((0, 1, 0)))
    return (loc, nrm) if ok else (None, None)


def ray_polar(theta, z):
    d = Vector((math.sin(theta), -math.cos(theta), 0.0))
    ok, loc, nrm, i = mom.ray_cast(Vector((AX.x, AX.y, z)) + d * 0.30, -d)
    return (loc, d) if ok else (None, d)


# --- the shared bevel: a flat cross-section with grooves (video 9:05: one edit grooves every lock)
prof_cu = bpy.data.curves.new("Hair2_Profile", "CURVE")
prof_cu.dimensions = "2D"
sp = prof_cu.splines.new("POLY")
NPR = 28
sp.points.add(NPR - 1)
for i in range(NPR):
    a = 2 * math.pi * i / NPR
    r = 1.0 + 0.02 * math.cos(4 * a)                       # grooves
    sp.points[i].co = (r * math.cos(a), r * math.sin(a) * 0.48, 0.0, 1.0)
sp.use_cyclic_u = True
PROFILE = bpy.data.objects.new("Hair2_Profile", prof_cu)
sc.collection.objects.link(PROFILE)
PROFILE.hide_render = True
PROFILE.hide_viewport = True


def material(name, lo, hi, rough=0.40, aniso=0.8, rot=0.25, tip=0.80, bump=0.15, edge=None):
    """Shading from the tutorial (video 12:25 to 17:19, frames 14:18 and 14:21 re-checked): noise stretched along the lock drives colour
    and a Bump (0.463 on screen), a gradient along the lock darkens the roots, and a gradient x noise mixes in a Transparent BSDF so the
    tips break into strands. UV x runs along the lock in 5.2 (checked: correlation 0.92)."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    out = N("ShaderNodeOutputMaterial")
    bs = N("ShaderNodeBsdfPrincipled")
    uv = N("ShaderNodeUVMap"); uv.uv_map = "UVMap"
    sep = N("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs[0], sep.inputs[0])

    def mul(src, k):
        m = N("ShaderNodeMath"); m.operation = "MULTIPLY"; m.inputs[1].default_value = k
        nt.links.new(src, m.inputs[0]); return m.outputs[0]

    def noise(ku, kv, scale, detail=5.0):
        c = N("ShaderNodeCombineXYZ")
        nt.links.new(mul(sep.outputs["X"], ku), c.inputs["X"])
        nt.links.new(mul(sep.outputs["Y"], kv), c.inputs["Y"])
        c.inputs["Z"].default_value = rng.uniform(0, 50)
        n = N("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        nt.links.new(c.outputs[0], n.inputs["Vector"])
        return n.outputs["Fac"]

    n1 = noise(2.5, 30.0, 1.0)                                   # streaks along the lock: colour
    n2 = noise(3.0, 110.0, 1.0)                                  # fine strands: bump
    oi = N("ShaderNodeObjectInfo")
    rnd = mul(oi.outputs["Random"], 0.30)
    root = mul(sep.outputs["X"], 0.28)                           # roots darker, ends lighter (video 14:02)

    def add(a, b):
        m = N("ShaderNodeMath"); m.operation = "ADD"
        nt.links.new(a, m.inputs[0]); nt.links.new(b, m.inputs[1]); return m.outputs[0]

    fac = add(add(n1, rnd), root)
    shift = N("ShaderNodeMath"); shift.operation = "SUBTRACT"; shift.inputs[1].default_value = 0.12
    nt.links.new(fac, shift.inputs[0])
    ramp = N("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*lo, 1.0)
    ramp.color_ramp.elements[1].color = (*hi, 1.0)
    nt.links.new(shift.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    bm = N("ShaderNodeBump")
    bm.inputs["Strength"].default_value = bump
    bm.inputs["Distance"].default_value = 0.002
    nt.links.new(n2, bm.inputs["Height"])
    nt.links.new(bm.outputs["Normal"], bs.inputs["Normal"])
    for k, v in (("Roughness", rough), ("Anisotropic", aniso), ("Anisotropic Rotation", rot),
                 ("Subsurface Weight", 0.04), ("Specular IOR Level", 0.6)):
        if k in bs.inputs:
            bs.inputs[k].default_value = v
    if "Subsurface Radius" in bs.inputs:
        bs.inputs["Subsurface Radius"].default_value = (0.5, 0.5, 0.5)
    # wispy edges: V runs around the lock, the flat sides are at V = 0, 0.5, 1 -> edge = 1 - |sin(2 pi V)|, broken up by noise
    vs = N("ShaderNodeMath"); vs.operation = "MULTIPLY"; vs.inputs[1].default_value = 6.2832
    nt.links.new(sep.outputs["Y"], vs.inputs[0])
    sn = N("ShaderNodeMath"); sn.operation = "SINE"; nt.links.new(vs.outputs[0], sn.inputs[0])
    ab = N("ShaderNodeMath"); ab.operation = "ABSOLUTE"; nt.links.new(sn.outputs[0], ab.inputs[0])
    inv_ = N("ShaderNodeMath"); inv_.operation = "SUBTRACT"; inv_.inputs[0].default_value = 1.0
    nt.links.new(ab.outputs[0], inv_.inputs[1])
    ed = add(inv_.outputs[0], mul(add(n2, mul(n1, -1.0)), 0.5))
    er = N("ShaderNodeValToRGB")
    er.color_ramp.elements[0].position = 0.80; er.color_ramp.elements[0].color = (0, 0, 0, 1)
    er.color_ramp.elements[1].position = 0.97; er.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(ed, er.inputs["Fac"])
    if edge is not None:
        er.color_ramp.elements[0].position = edge
        er.color_ramp.elements[1].position = min(0.99, edge + 0.17)
    if tip is None:
        tr0 = N("ShaderNodeBsdfTransparent"); mx0 = N("ShaderNodeMixShader")
        nt.links.new(er.outputs["Color"], mx0.inputs["Fac"])
        nt.links.new(bs.outputs[0], mx0.inputs[1]); nt.links.new(tr0.outputs[0], mx0.inputs[2])
        nt.links.new(mx0.outputs[0], out.inputs["Surface"])
    else:
        tx = N("ShaderNodeMath"); tx.operation = "ADD"
        nt.links.new(sep.outputs["X"], tx.inputs[0])
        dn = N("ShaderNodeMath"); dn.operation = "SUBTRACT"; dn.inputs[1].default_value = 0.5
        nt.links.new(n1, dn.inputs[0])
        dn2 = mul(dn.outputs[0], 0.45)
        nt.links.new(dn2, tx.inputs[1])
        r2 = N("ShaderNodeValToRGB")
        r2.color_ramp.elements[0].position = tip
        r2.color_ramp.elements[0].color = (0, 0, 0, 1)
        r2.color_ramp.elements[1].position = min(1.0, tip + 0.16)
        r2.color_ramp.elements[1].color = (1, 1, 1, 1)
        nt.links.new(tx.outputs[0], r2.inputs["Fac"])
        tr = N("ShaderNodeBsdfTransparent")
        mx = N("ShaderNodeMixShader")
        mxf = N("ShaderNodeMath"); mxf.operation = "MAXIMUM"
        nt.links.new(r2.outputs["Color"], mxf.inputs[0]); nt.links.new(er.outputs["Color"], mxf.inputs[1])
        nt.links.new(mxf.outputs[0], mx.inputs["Fac"])
        nt.links.new(bs.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return mat


M_TOP = material("Lock_Top", (0.07, 0.03, 0.009), (0.22, 0.11, 0.032), rough=0.75, aniso=0.0, tip=0.9)
M_BANG = material("Lock_Bang", (0.19, 0.08, 0.025), (0.46, 0.23, 0.06))
M_STREAK = material("Lock_Streak", (0.46, 0.27, 0.10), (0.74, 0.50, 0.24), rough=0.35)
M_LOW = material("Lock_Low", (0.05, 0.02, 0.006), (0.16, 0.075, 0.022), rough=0.75, aniso=0.0)
M_BUN = material("Lock_Bun", (0.025, 0.011, 0.004), (0.09, 0.04, 0.013), rough=0.8, aniso=0.0, tip=None)
count = {"n": 0}
PATHS = []                                                      # (name, points) of every lock, for the outer strand layer


def lock(name, pts, r0, r1, mat, twist=0.0, tip=0.15, root=0.35, tipstart=0.85, visible=True, store=None):
    pts = np.asarray(pts, dtype=float)
    if not visible:                                   # path only: the strand layer is built from it, no flat ribbon is made
        PATHS.append((name, (store if store is not None else pts).copy()))
        return None
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = 6
    cu.bevel_mode = "OBJECT"
    cu.bevel_object = PROFILE
    cu.use_fill_caps = True
    if hasattr(cu, 'use_uv_as_generated'):
        cu.use_uv_as_generated = True
    s = cu.splines.new("NURBS")
    s.points.add(len(pts) - 1)
    n = len(pts)
    for i, p in enumerate(pts):
        t = i / (n - 1)
        s.points[i].co = (p[0], p[1], p[2], 1.0)
        rr = r0 + (r1 - r0) * t
        rt = root + (1.0 - root) * min(1.0, t / 0.18)                                        # thin roots (hand test: Alt+S 0.35 on points 0 and 1)
        s.points[i].radius = rr * rt * (1.0 - (1.0 - tip) * max(0.0, (t - tipstart) / (1.0 - tipstart)))        # taper to a tip
        s.points[i].tilt = twist * t
    s.order_u = 4
    s.use_endpoint_u = True
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    sc.collection.objects.link(ob)
    count["n"] += 1
    PATHS.append((name, (store if store is not None else pts).copy()))
    return ob


def path_to_bun(R, n=10, length=0.145, lift0=0.012, lift_mid=0.012, target=None):
    tgt = BUN if target is None else target
    p = Vector(R)
    out = [p.copy()]
    step = length / (n - 1)
    for k in range(1, n):
        d = (tgt - p).normalized()
        w = 1.0 - k / (n - 1)
        d = (d * (1 - 0.25 * w) + Vector((0, 0, 1)) * 0.25 * w).normalized()
        q = p + d * step
        z0 = ray_down(q.x, q.y)
        if z0 is not None:
            lim = z0.z + lift0 + lift_mid * math.sin(math.pi * k / (n - 1))
            q.z = max(q.z, lim)
        q = p + (q - p).normalized() * step
        out.append(q); p = q
    return np.array(out)



def clear_surface(p, d=0.005):
    """keep a point at least d above the skin (push out along the normal if inside or too close)"""
    ok, loc, nrm, i = mom.closest_point_on_mesh(Vector(p))
    if not ok:
        return np.asarray(p, dtype=float)
    v = Vector(p) - loc
    if v.dot(nrm) < 0 or v.length < d:
        return np.array(loc + nrm * d)
    return np.asarray(p, dtype=float)


def bez(P0, P1, P2, n=9):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * P0 + 2 * (1 - t) * t * P1 + t ** 2 * P2


# ---------------- ONE HAIR MASS (Nick, 15 Nov: "think of her hair as one connected clump, not different groups")
# Every strand grows from a root on the scalp. Above the half-up line it sweeps back and up into the bun, below it it hangs, and in between
# the path is blended smoothly from one to the other (a fan), so there are no seams. Reference 62.0 s / 35.0 s: the swept band ends at about
# ear-top height and the hanging hair starts right under it. Roots near the ear hang BEHIND the ear.
M_MID = material("Lock_Mid", (0.04, 0.016, 0.005), (0.13, 0.06, 0.018), rough=0.75, aniso=0.0, tip=0.9)
Z_LINE, Z_BAND = 1.588, 0.026                      # my plan: swept weight rises from 0 at z 1.576 to 1 at z 1.616


sc.cycles.transparent_max_bounces = 32; sc.cycles.max_bounces = 16                      # ribbons and strands have transparent edges/tips (default 8 gave dark patches)
P_GAP = globals().get('P_GAP', -0.020); P_FLARE = globals().get('P_FLARE', 0.0); P_CURL = globals().get('P_CURL', 0.85); P_ZEND = globals().get('P_ZEND', 0.035); P_GAP2 = globals().get('P_GAP2', -0.035)


def smooth01(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def rs(P, n=12):
    P = np.asarray(P, dtype=float)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    u = np.linspace(0, seg[-1], n)
    return np.stack([np.interp(u, seg, P[:, k]) for k in range(3)], axis=1)


def hang_path(R, d, th_deg, z0, n=12, side=1):
    """Hair that rests ON the body: each point sits on the real skull / neck / shoulder surface (a ray from outside at that height and angle)
    plus a little volume, so the silhouette follows head -> nape -> shoulders (it narrows at the neck) instead of hanging from the widest part
    of the skull. Ends curl in toward the surface. Neighbouring strands share their swing phase (th), so the flow is coherent."""
    th = math.radians(th_deg)
    z_end = (1.425 + P_ZEND - 0.026 * math.cos(3 * th) - 0.024 * math.sin(7 * th + z0 * 30) - 0.045 * rng.random()
             - (0.040 if int(th_deg / 4) % 2 == 0 else 0.0)
             + 0.045 * (1 - smooth01(th_deg / 110.0))
             - 0.030 * smooth01((th_deg - 120.0) / 60.0))
    ph = 2.6 * th
    pts = []
    last = np.array(R, dtype=float)
    for s_ in np.linspace(0, 1, n):
        zz = R[2] + (z_end - R[2]) * s_
        loc, dd = ray_polar(side * th, zz)
        if loc is None:
            base = last.copy(); base[2] = zz; nrm = np.array([d.x, d.y, 0.0])
        else:
            base = np.array(loc); nrm = np.array([dd.x, dd.y, 0.0])
        full = 0.005 + 0.012 * math.exp(-((s_ - 0.18) / 0.20) ** 2)                    # puff at the roots, then fall close (article: avoid outward sticking)
        full += (P_GAP + P_GAP2 * smooth01((th_deg - 100.0) / 50.0)) * smooth01((s_ - 0.12) / 0.45)                                    # air gap behind the neck (hair hangs free, does not hug the nape)
        full += P_FLARE * smooth01((s_ - 0.70) / 0.30)                                  # ends flare out
        full *= (1.0 - P_CURL * smooth01((s_ - 0.80) / 0.20))                           # ends curl in toward the surface
        tang = np.array([dd.y, -dd.x, 0.0]) if loc is not None else np.array([d.y, -d.x, 0.0])
        wav = 0.010 * math.sin(2.0 * math.pi * s_ + ph) * s_ + 0.004 * math.sin(4 * math.pi * s_ + 2 * ph + rng.uniform(-0.3, 0.3)) * s_
        p = base + nrm * full + tang * wav
        pts.append(p); last = p
    return np.array(pts)


def ear_hang_path(side, th_deg, z0, n=12):
    pts = []
    for th_d in np.linspace(th_deg, 134, 8):
        zz = z0 - 0.078 * max(0.0, (th_d - 92) / 42.0) ** 1.2                      # sweeps back above the ear, drops behind it
        loc, d = ray_polar(side * math.radians(th_d), zz)
        if loc is None:
            return None
        pts.append(np.array(loc) + np.array([d.x, d.y, 0.0]) * 0.010)
    last = pts[-1]
    z_end = 1.452 - 0.040 * rng.random() - (0.045 if int(th_deg / 4) % 2 == 0 else 0.0)
    for s_ in np.linspace(0.25, 1.0, 5):
        pts.append(np.array([last[0], last[1] + 0.008 * s_, last[2] + (z_end - last[2]) * s_]))
    return rs(pts, n)


def bun_path(R, n=12):
    dist = (BUN - Vector(R)).length
    extra = 0.014 * math.exp(-(R[0] / 0.11) ** 2) if R[1] < -0.03 else 0.0          # crown dome
    tgt = Vector((BUN.x + R[0] * 0.30 + rng.uniform(-0.003, 0.003), BUN.y, BUN.z + max(-0.012, min(0.012, 0.35 * (R[2] - 1.62)))))   # ordered targets: strands converge without crossing
    return np.asarray(path_to_bun(Vector(R), n=n, length=max(0.03, min(0.15, dist * 1.12)), lift0=0.005, lift_mid=0.007 + extra * 0.6, target=tgt))


FIELD = []


def add_field(R, d, side, th_deg, z0):
    w = smooth01((R[2] - Z_LINE) / Z_BAND)
    if th_deg < 78:
        w = 1.0                                                                    # nothing hangs in front of the ear: swept back into the bun band
    bun = bun_path(R)
    if w > 0.999:
        P = bun
    else:
        hang = ear_hang_path(side, th_deg, z0) if 72 <= th_deg <= 108 else hang_path(R, d, th_deg, z0, side=side)
        if hang is None:
            return
        P = (1 - w) * hang + w * bun                                              # continuous fan between hanging and swept
    P = np.array([clear_surface(p, 0.005) if p[2] > 1.50 else p for p in P])
    FIELD.append((R, d, side, th_deg, w, P))


def make_field_locks():
    n = len(FIELD)
    roots = np.array([f[5][0] for f in FIELD]); paths = np.array([f[5] for f in FIELD])
    # Blend Hair Curves: each strand = 55% itself + 45% mean of its 6 nearest neighbours' offsets from their own roots (flow becomes coherent, strays are pulled in)
    rel = paths - roots[:, None, :]
    out = paths.copy()
    for i in range(n):
        dist = np.linalg.norm(roots - roots[i], axis=1)
        idx = np.argsort(dist)[1:7]
        out[i] = roots[i] + 0.55 * rel[i] + 0.45 * rel[idx].mean(0)
    # Smooth Hair Curves: 3 iterations, roots locked
    for _ in range(3):
        out[:, 1:-1] = (out[:, :-2] + 2 * out[:, 1:-1] + out[:, 2:]) / 4.0
    for (R, d, side, th_deg, w, _P), P in zip(FIELD, out):
        _emit(R, d, side, th_deg, w, P)


def _emit(R, d, side, th_deg, w, P):
    bk = 0 if w > 0.66 else (1 if w > 0.12 else 2)
    r0 = 0.0050 * rng.uniform(0.85, 1.2)                                           # ribbons narrower than the strand bundle
    radial = P - np.array([0.0, -0.06, 1.55]); radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
    Pin = P - radial * 0.003                                                       # and 3 mm inside it, so they stay hidden
    lock(f"Lock_F{bk}_{side:+d}_{th_deg:.0f}_{R[2]:.3f}_{R[0]:+.3f}", Pin, r0, r0 * 0.85, (M_TOP, M_MID, M_LOW)[bk],
         twist=rng.uniform(-0.4, 0.4), tip=0.2 - 0.1 * (1 - w), tipstart=0.85 - 0.15 * (1 - w), root=0.75, store=P)


for side in (-1, 1):
    for th0 in np.arange(0, 181, 5.0):
        if side == -1 and th0 in (0.0, 180.0):
            continue
        for z0 in np.arange(1.500, 1.656, 0.0105):
            z = z0 + rng.uniform(-0.003, 0.003); thj = float(np.clip(th0 + rng.uniform(-1.5, 1.5), 0.0, 180.0))
            if 72 <= thj <= 108 and z < 1.574:
                continue                                                        # her ear stays free
            if thj < 48 and z < 1.618:
                continue
            if 48 <= thj < 72 and z < 1.585:
                continue                                                        # nothing hangs from in front of the ear (the face-framing pieces do that)
            loc, d = ray_polar(side * math.radians(thj), z)
            if loc is None:
                continue
            R = np.array(loc)
            if thj < 48 and R[2] < 1.618:
                continue                                                        # forehead: the bangs
            if R[2] > 1.656 or R[2] < 1.49:
                continue
            add_field(R, d, side, thj, z)
for side in (-1, 1):                                                            # extra roots right above the ear (a bare patch showed there)
    for th0 in np.arange(70, 111, 4.0):
        for z0 in np.arange(1.574, 1.640, 0.0065):
            loc, d = ray_polar(side * math.radians(th0), z0)
            if loc is not None:
                add_field(np.array(loc), d, side, float(th0), z0)
for x in np.linspace(-0.066, 0.066, 12):                                        # crown roots seen from above
    for y in np.linspace(-0.13, 0.0, 10):
        s0 = ray_down(x + rng.uniform(-0.003, 0.003), y + rng.uniform(-0.003, 0.003))
        if s0 is None or s0.z < 1.632:
            continue
        add_field(np.array(s0), Vector((0, 1, 0)), 1 if x >= 0 else -1, 0.0, s0.z)

# ---------------- BANGS: from the ROOT at the part, the hair rises up and forward in an arc, then falls over the forehead and sweeps to the cheekbones
# (Nick, 15 Nov: "hers orbit upwards first and then go down"; reference 64.5 s, 55.5 s)
for side in (-1, 1):
    for k in range(18):
        xr = side * (0.012 + 0.0030 * k)
        s0 = ray_down(xr, -0.095)
        if s0 is None:
            continue
        P0 = np.array([s0.x, s0.y, s0.z + 0.002])
        P1 = np.array([xr * 1.35 + side * 0.012, P0[1] - (0.050 + 0.020 * rng.random()), P0[2] + 0.030 + 0.012 * rng.random()])
        xe = side * min(abs(xr) + 0.004 + 0.0016 * k + 0.006 * rng.random(), 0.072); ze = 1.559 - 0.010 * rng.random() - 0.0006 * k          # curtain: inner locks fall near the part, outer locks sweep out to the cheekbone
        loc, nrm = ray_face(xe, ze)
        if loc is None:
            continue
        P2 = np.array([xe, loc.y - 0.010, ze])
        pts = [clear_surface(p) for p in bez(P0, P1, P2)]
        streak = k in (2, 9)
        lock(f"Lock_Bang_{side:+d}_{k}", pts, 0.0078 if streak else 0.0086, 0.0044, M_STREAK if streak else M_BANG, twist=0.2, tip=0.04, tipstart=0.5)

# ---------------- FOREHEAD CLUMPS: same arc, falling straighter over the forehead to the brow line (reference 64.5 s; article: hairline/partings)
for i in range(15):
    side = -1 if i % 2 else 1
    xr = side * rng.uniform(0.003, 0.036)
    s0 = ray_down(xr, -0.100)
    if s0 is None:
        continue
    P0 = np.array([s0.x, s0.y, s0.z + 0.002])
    P1 = np.array([xr, P0[1] - 0.060, P0[2] + 0.028])
    xe = xr + side * rng.uniform(-0.004, 0.014); ze = rng.choice((1.588, 1.580, 1.570, 1.560, 1.550, 1.575))
    loc, nrm = ray_face(xe, ze)
    if loc is None:
        continue
    P2 = np.array([xe, loc.y - 0.009, ze])
    pts = [clear_surface(p) for p in bez(P0, P1, P2)]
    lock(f"Lock_Fore_{i}", pts, rng.uniform(0.0046, 0.0068), 0.0028, M_BANG, twist=rng.uniform(-0.3, 0.3), tip=0.04, tipstart=0.45, root=0.5)

# the bun is the SAME hair as beside it (lit frame t=73 s: bun L 41.7 vs hair L 42.3; dark frame t=16 s: 11.3 vs 11.3)
# ---------------- BUN: six thin twisted locks wound in a spiral, dark, low at the back of the crown (62.0 s, 35.0 s)
C0 = np.array([0.0, 0.050, 1.628])
for j in range(10):
    ph = j * 2 * math.pi / 10
    pts = []
    for s in np.linspace(0, 1, 24):
        ang = ph + 2 * math.pi * 1.6 * s
        R = 0.027 * (1 - 0.84 * s)
        pts.append([(j - 2.5) * 0.004 * (1 - 0.6 * s), C0[1] + R * math.cos(ang), C0[2] + R * math.sin(ang)])
    lock(f"Lock_Bun_{j}", pts, 0.0072, 0.0048, M_BUN, twist=2 * math.pi * 1.5, tip=0.12, root=1.0, tipstart=0.8, visible=False)

for j in range(8):                                          # dense core so the knot has no hollow centre (reference 62.0 s)
    ph = j * 2 * math.pi / 8
    pts = []
    for s in np.linspace(0, 1, 18):
        ang = ph + 2 * math.pi * 1.3 * s
        R = 0.014 * (1 - 0.8 * s)
        pts.append([(j - 2) * 0.0045, C0[1] + R * math.cos(ang), C0[2] + R * math.sin(ang)])
    lock(f"Lock_BunCore_{j}", pts, 0.0082, 0.0056, M_BUN, twist=2 * math.pi, tip=0.3, root=1.0, visible=False)

# (face-framing pieces removed 15 Nov: in her side frame there is no hair in front of the ear)

make_field_locks()

# ---------------- SCALP CAP: a thin dark cap on the head so no skin shows between hairs (article: base layer; ear and face left free)
import bmesh
_old = bpy.data.objects.get("Hair2_Cap")
if _old:
    bpy.data.objects.remove(_old, do_unlink=True)
_me = mom.data.copy()
_bm = bmesh.new(); _bm.from_mesh(_me)
_rem = [v for v in _bm.verts if (v.co.z < 1.52 or (abs(v.co.x) > 0.062 and -0.085 < v.co.y < -0.032 and v.co.z < 1.578)
                                  or (v.co.y < -0.095 and v.co.z < 1.628))]
bmesh.ops.delete(_bm, geom=_rem, context="VERTS")
_bm.normal_update()
for _v in _bm.verts:
    _v.co += _v.normal * 0.0016
_bm.to_mesh(_me); _bm.free()
_cap = bpy.data.objects.new("Hair2_Cap", _me)
sc.collection.objects.link(_cap)
_cap.parent = mom
_cm = bpy.data.materials.get("Hair2_CapMat") or bpy.data.materials.new("Hair2_CapMat")
_cm.use_nodes = True
for _n in _cm.node_tree.nodes:
    if _n.type == "BSDF_PRINCIPLED":
        _n.inputs["Base Color"].default_value = (0.045, 0.02, 0.008, 1.0)
        _n.inputs["Roughness"].default_value = 0.7
_me.materials.clear(); _me.materials.append(_cm)
print("scalp cap:", len(_me.vertices), "vertices")

# ---------------- FLOATING strands: sparse thin separate curves on the outside of the top layer (video 9:52 to 10:12; article: flyaways)
M_FLY = material("Lock_Fly", (0.30, 0.16, 0.05), (0.62, 0.38, 0.14), rough=0.35, tip=0.55)
for i in range(70):
    th = rng.uniform(-math.pi * 0.95, math.pi * 0.95)
    z = rng.uniform(1.58, 1.655)
    loc, d = ray_polar(th, z)
    if loc is None or loc.z < 1.575:
        continue
    R = Vector(loc)
    P = path_to_bun(R, n=9, length=rng.uniform(0.06, 0.14), lift0=0.016, lift_mid=0.018)
    P = P + np.array([0.0, 0.0, 0.0])
    ph = rng.uniform(0, 6.28)
    for k in range(len(P)):
        P[k] += np.array([math.sin(ph + k * 0.9) * 0.003, math.cos(ph + k * 0.7) * 0.003, 0.0]) * (k / len(P))
    lock(f"Lock_Fly_{i}", P, 0.0016, 0.0010, M_FLY, twist=0.0, tip=0.4)

# ---------------- OUTER STRAND LAYER: fine hair on top of the locks (article: "an opaque underlayer for volume, finer outer layers for visible
# strands, and flyaways"; manual Principled Hair: Huang model for human hair, Random Color / Random Roughness vary strands, Coat is for fur)
def srgb_lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hair_mat(name, mel, red, rough=0.32, aspect=0.75, ombre=0.0, tint=None, direct=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    h = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
    h.parametrization = "MELANIN"
    h.model = "HUANG"
    for k, v in (("Melanin", mel), ("Melanin Redness", red), ("Roughness", rough), ("Aspect Ratio", aspect),
                 ("Random Color", 0.05), ("Random Roughness", 0.06)):
        if k in h.inputs:
            h.inputs[k].default_value = v
    if direct is not None:                          # DIRECT colour measured from the reference (melanin cannot reach her golden chroma): (root sRGB, tip sRGB)
        h.parametrization = "COLOR"
        hi2 = nt.nodes.new("ShaderNodeHairInfo"); mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
        mx.inputs[6].default_value = (*[srgb_lin(c) for c in direct[0]], 1.0); mx.inputs[7].default_value = (*[srgb_lin(c) for c in direct[1]], 1.0)
        nt.links.new(hi2.outputs["Intercept"], mx.inputs[0]); nt.links.new(mx.outputs[2], h.inputs["Color"])
        ombre = 0.0
    if tint is not None and "Tint" in h.inputs:
        h.inputs["Tint"].default_value = (*tint, 1.0)
    if ombre:
        hi = nt.nodes.new("ShaderNodeHairInfo")
        ma = nt.nodes.new("ShaderNodeMath"); ma.operation = "MULTIPLY_ADD"
        ma.inputs[1].default_value = -ombre
        ma.inputs[2].default_value = mel
        nt.links.new(hi.outputs["Intercept"], ma.inputs[0])
        nt.links.new(ma.outputs[0], h.inputs["Melanin"])
    nt.links.new(h.outputs[0], o.inputs["Surface"])
    return mat


for n in list(bpy.data.objects.keys()):
    if n.startswith("Hair2_Outer"):
        bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
CEN = Vector((0.0, -0.06, 1.55))
is_streak = lambda n: n.startswith("Lock_Bang_") and (n.endswith("_2") or n.endswith("_9"))
GROUPS = (("Hair2_Outer_Top", ("Lock_F0_",), hair_mat("Hair2O_Top", 0.14, 1.00, rough=0.40, direct=((138, 88, 46), (190, 126, 66))), 110, 0.0030, 0.003, lambda n: True),
          ("Hair2_Outer_Mid", ("Lock_F1_",), hair_mat("Hair2O_Mid", 0.56, 0.85, rough=0.45, direct=((55, 34, 20), (82, 54, 33))), 90, 0.0030, 0.003, lambda n: True),
          ("Hair2_Outer_Low", ("Lock_F2_",), hair_mat("Hair2O_Low", 0.54, 0.88, direct=((52, 36, 25), (84, 60, 44))), 100, 0.0030, 0.003, lambda n: True),
          ("Hair2_Outer_Bun", ("Lock_Bun_", "Lock_BunCore_"), hair_mat("Hair2O_Bun", 0.95, 0.40, rough=0.45, direct=((112, 70, 38), (150, 98, 54))), 160, 0.0034, 0.003, lambda n: True),
          ("Hair2_Outer_Bang", ("Lock_Bang_", "Lock_Piece_"), hair_mat("Hair2O_Bang", 0.52, 0.68, direct=((120, 82, 48), (168, 118, 66))), 230, 0.0040, 0.004, lambda n: not is_streak(n)),
          ("Hair2_Outer_Fore", ("Lock_Fore_",), hair_mat("Hair2O_Fore", 0.52, 0.68, direct=((120, 82, 48), (168, 118, 66))), 60, 0.0030, 0.004, lambda n: True),
          ("Hair2_Outer_Streak", ("Lock_Bang_",), hair_mat("Hair2O_Streak", 0.14, 0.36, direct=((190, 150, 95), (236, 202, 142))), 80, 0.0030, 0.005, is_streak))
nrng = np.random.default_rng(5)
for gname, prefixes, gmat, n_per, spread, lift, flt in GROUPS:
    allc = []
    for pname, P in PATHS:
        if not pname.startswith(prefixes) or not flt(pname):
            continue
        seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
        uu = np.linspace(0, seg[-1], 12)
        P = np.stack([np.interp(uu, seg, P[:, k]) for k in range(3)], axis=1)           # same point count for every path
        seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]            # arc length of the resampled path
        tang = np.gradient(P, axis=0)
        tang /= np.maximum(np.linalg.norm(tang, axis=1, keepdims=True), 1e-9)
        out = P - np.array(CEN)
        out /= np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-9)
        t = np.linspace(0, 1, len(P))[:, None]
        for _ in range(n_per):
            frac = nrng.uniform(0.97, 1.0) if gname in ("Hair2_Outer_Bang", "Hair2_Outer_Fore", "Hair2_Outer_Streak") else nrng.uniform(0.80, 1.0)   # a fringe reaches the brow: no shortening
            st = nrng.uniform(0.0, 0.035)                                  # nearly from the root, so ribbon roots stay covered
            Q = np.stack([np.interp(np.linspace(seg[-1] * st, seg[-1] * frac, 12), seg, P[:, k]) for k in range(3)], axis=1)
            r = nrng.normal(0, spread, 3)
            perp = np.stack([r - tang[i] * (tang[i] @ r) for i in range(len(P))])
            child = Q + perp * (1.0 - 0.25 * t) + out * lift + nrng.normal(0, 0.0004, P.shape) * t
            allc.append(child)
    if not allc:
        print(f"{gname}: no matching paths, skipped")
        continue
    C = np.array(allc)
    NN, per = C.shape[0], C.shape[1]
    cd = bpy.data.hair_curves.new(gname)
    cd.add_curves([per] * NN)
    cd.attributes["position"].data.foreach_set("vector", C.reshape(-1).astype(np.float32))
    rad = cd.attributes.get("radius") or cd.attributes.new("radius", "FLOAT", "POINT")
    rad.data.foreach_set("value", np.full(NN * per, 0.00006, dtype=np.float32))
    cd.surface = mom
    cd.surface_uv_map = "UVMap"
    oo = bpy.data.objects.new(gname, cd)
    sc.collection.objects.link(oo)
    oo.parent = mom
    cd.materials.append(gmat)
    print(f"{gname}: {NN} strands x {per} points")
print("locks built:", count["n"])
