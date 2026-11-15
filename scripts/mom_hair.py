"""The mom's hair from scratch: a half-up bun, read from the reference clip (35.0 s back, 62.0 s side-back,
64.5 s front, 18.0 s three-quarter).

Method (the particle-hair tutorial, scripted on Blender's Curves hair): a painted density map on the scalp,
guide strands shaped by code instead of combed by hand, then interpolated children around the guides.
Strands are kept outside the skin by pushing every point out of the body mesh (so hanging hair falls
freely instead of being glued to the face).

Sections (numbers as on the analysis sheet):
  1 bun     a small coiled bun high on the back of the crown, darker
  2 top     swept straight back from the hairline into the bun, with lift at the crown
  3 lower   the lower half left down, straight, to the collar
  4 bangs   long wispy curtain bangs from a near-centre part, ending at the cheekbones
  5 pieces  face-framing pieces in front of the ears, to the jaw, ends flicking out
  6 colour  honey blonde, darker roots and underside, platinum streaks in the bangs
Everything is built in the rest pose (character faces -Y) and parented to the head bone.
"""
import os
import time

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from recipes import haircut, human, materials, sculpt
from recipes import hair as hair_mod
from recipes import rig as _rig

env = lambda k, d: type(d)(os.environ.get(k, d))
sig = haircut._sigmoid
N_PTS = 18


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


class Body:
    """The skin in the rest pose, for keeping strands outside it."""

    def __init__(self, base_verts):
        v = human.to_blender(base_verts)
        faces = [f for f in human.base_mesh()[2] if all(i < human.BODY_VERTS for i in f)]
        self.bvh = BVHTree.FromPolygons([Vector(p) for p in v], faces)
        top = v[:human.BODY_VERTS][:, 2].max()
        q, n, _, _ = self.bvh.find_nearest(Vector((0.0, 0.0, top + 0.3)))
        self.sign = 1.0 if np.dot(np.array((0.0, 0.0, top + 0.3)) - np.array(q), np.array(n)) > 0 else -1.0

    def push(self, P, clear):
        out = P.copy()
        for i, p in enumerate(P):
            q, n, _, _ = self.bvh.find_nearest(Vector(p))
            if q is None:
                continue
            n = np.array(n) * self.sign
            depth = float(np.dot(p - np.array(q), n))
            if depth < clear[i]:
                out[i] = p + n * (clear[i] - depth)
        return out


def resample(strands, n=N_PTS):
    out = np.zeros((len(strands), n, 3))
    for i, P in enumerate(strands):
        P = np.asarray(P)
        s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
        if s[-1] < 1e-6:
            out[i] = P[0]
            continue
        u = np.linspace(0.0, s[-1], n)
        for k in range(3):
            out[i, :, k] = np.interp(u, s, P[:, k])
    return out


def grow(body, roots, normals, direction, stop, clearance, seg=0.005, max_steps=90):
    """March every strand: step along `direction`, then push out of the skin by `clearance`."""
    n = len(roots)
    cur = body.push(roots + normals * 0.002, clearance(roots, np.zeros(n)))
    paths = [[r.copy(), c.copy()] for r, c in zip(roots, cur)]
    travelled = np.zeros(n)
    live = np.ones(n, bool)
    for _ in range(max_steps):
        idx = np.where(live)[0]
        if not len(idx):
            break
        d = unit(direction(cur[idx], travelled[idx], idx))
        nxt = cur[idx] + d * seg
        nxt = body.push(nxt, clearance(nxt, travelled[idx] + seg, idx))
        travelled[idx] += np.linalg.norm(nxt - cur[idx], axis=1)
        cur[idx] = nxt
        for j, i in enumerate(idx):
            paths[i].append(nxt[j].copy())
        done = stop(cur[idx], travelled[idx], idx)
        live[idx[done]] = False
    return resample(paths)


def children(body, guides, roots, clump, frizz, clear, seed, k=4, pull_to=None):
    """Children copy the weighted shape of their nearest guides, clump toward their own guide's tip,
    get a little frizz, and are kept outside the skin."""
    rng = np.random.default_rng(seed)
    g_roots = guides[:, 0]
    shapes = guides - g_roots[:, None, :]
    t = np.linspace(0.0, 1.0, guides.shape[1])[None, :, None]
    out = np.zeros((len(roots), guides.shape[1], 3))
    for lo in range(0, len(roots), 4096):
        r = roots[lo:lo + 4096]
        d = np.linalg.norm(r[:, None, :] - g_roots[None, :, :], axis=2)
        idx = np.argsort(d, axis=1)[:, :k]
        w = 1.0 / np.maximum(np.take_along_axis(d, idx, axis=1), 1e-4) ** 2
        w /= w.sum(axis=1, keepdims=True)
        s = r[:, None, :] + (shapes[idx] * w[:, :, None, None]).sum(axis=1)
        own = guides[idx[:, 0]]
        s = s + (own - s) * (clump * t ** 1.5)
        s = s + rng.normal(size=s.shape) * frizz * t
        if pull_to is not None:                       # top section: every strand ends in the bun
            s = s + (pull_to - s[:, -1:, :]) * t ** 3 * 0.85
        out[lo:lo + 4096] = s
    flat = out.reshape(-1, 3)
    tt = np.tile(np.linspace(0.0, 1.0, guides.shape[1]), len(roots))
    flat = body.push(flat, clear(tt))
    return flat.reshape(out.shape)


def hair_material(name, melanin, redness, root=0.08, rough=0.30):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N, L = mat.node_tree.nodes, mat.node_tree.links
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    for n in list(N):
        if n.type == "BSDF_PRINCIPLED":
            N.remove(n)
    h = N.new("ShaderNodeBsdfHairPrincipled")
    h.parametrization = "MELANIN"
    h.inputs["Melanin Redness"].default_value = redness
    h.inputs["Roughness"].default_value = rough
    h.inputs["Radial Roughness"].default_value = 0.4
    h.inputs["Random Roughness"].default_value = 0.3
    if "Random Color" in h.inputs:
        h.inputs["Random Color"].default_value = 0.2
    info = N.new("ShaderNodeHairInfo")
    mr = N.new("ShaderNodeMapRange")                  # darker at the root, fading out over the first 30 %
    L.new(info.outputs["Intercept"], mr.inputs["Value"])
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.0, 0.3
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = melanin + root, melanin
    L.new(mr.outputs["Result"], h.inputs["Melanin"])
    L.new(h.outputs["BSDF"], out.inputs["Surface"])
    return mat


def build(scene, mom, name, strands, mat, radius):
    obj = haircut.build(scene, name, strands.astype(np.float32), np.zeros(len(strands)), mat, radius=radius)
    _rig.parent_to_bone(obj, mom, "head")
    return obj


HAIR_ASSETS = os.path.join(bpy.utils.resource_path("LOCAL"), "datafiles", "assets", "nodes", "procedural_hair_node_assets.blend")
# per section: Blender's own Clump, Noise and Frizz, then a tapered profile (Nick, 14 Nov: "Yes, hair nodes")
TEXTURE = {
    "top":     dict(clump=(0.008, 0.55, 0.30, 0.001), noise=(0.0015, 25.0), frizz=0.0008),
    "lower":   dict(clump=(0.010, 0.80, 0.40, 0.003), noise=(0.0040, 18.0), frizz=0.0015, curl=True),   # ends flip out (Nick, 14 Nov)
    "bangs":   dict(clump=(0.006, 0.90, 0.60, 0.002), noise=(0.0030, 22.0), frizz=0.0010),
    "streaks": dict(clump=(0.006, 0.90, 0.60, 0.002), noise=(0.0030, 22.0), frizz=0.0010),
    "pieces":  dict(clump=(0.008, 0.90, 0.50, 0.002), noise=(0.0040, 18.0), frizz=0.0012),
    "bun":     dict(clump=None, noise=(0.0020, 40.0), frizz=0.0020),
}


def _hair_group(name):
    if name not in bpy.data.node_groups:
        with bpy.data.libraries.load(HAIR_ASSETS, link=False) as (src, dst):
            dst.node_groups = [name]
    return bpy.data.node_groups[name]


def _set(node, name, value):
    sock = next((i for i in node.inputs if i.name == name), None)
    if sock is None:
        raise KeyError(f"{node.node_tree.name} has no input {name!r}")
    sock.default_value = value


def add_texture(obj, section):
    """Geometry nodes on one hair object: Clump -> Noise -> Frizz -> Set Hair Curve Profile."""
    t = TEXTURE[section]
    k = env("TEX", 1.0)                                  # one knob to scale every effect (0 = off)
    tree = bpy.data.node_groups.new(f"HairTexture_{section}", "GeometryNodeTree")
    tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    gin, gout = tree.nodes.new("NodeGroupInput"), tree.nodes.new("NodeGroupOutput")
    chain = []
    if t["clump"]:
        n = tree.nodes.new("GeometryNodeGroup"); n.node_tree = _hair_group("Clump Hair Curves")
        dist, fac, shape, spread = t["clump"]
        _set(n, "Guide Distance", dist); _set(n, "Factor", fac * min(k, 1.0)); _set(n, "Shape", shape)
        _set(n, "Tip Spread", spread); _set(n, "Existing Guide Map", False); _set(n, "Preserve Length", True)
        chain.append(n)
    if t.get("curl") and env("CURL", 1):
        n = tree.nodes.new("GeometryNodeGroup"); n.node_tree = _hair_group("Curl Hair Curves")
        _set(n, "Curl Start", env("CURL_START", 0.70)); _set(n, "Radius", env("CURL_R", 0.014))
        _set(n, "Frequency", env("CURL_FREQ", 0.6)); _set(n, "Factor Start", 0.0); _set(n, "Factor End", 1.0)
        _set(n, "Random Offset", env("CURL_RANDOM", 0.6)); _set(n, "Existing Guide Map", False)
        chain.append(n)
    n = tree.nodes.new("GeometryNodeGroup"); n.node_tree = _hair_group("Hair Curves Noise")
    _set(n, "Distance", t["noise"][0] * k); _set(n, "Scale", t["noise"][1]); _set(n, "Preserve Length", True)
    chain.append(n)
    n = tree.nodes.new("GeometryNodeGroup"); n.node_tree = _hair_group("Frizz Hair Curves")
    _set(n, "Distance", t["frizz"] * k); _set(n, "Preserve Length", True)
    chain.append(n)
    n = tree.nodes.new("GeometryNodeGroup"); n.node_tree = _hair_group("Set Hair Curve Profile")
    _set(n, "Radius", env("HAIR_RADIUS", 0.00006)); _set(n, "Shape", 0.5)
    chain.append(n)
    prev = gin.outputs[0]
    for n in chain:
        tree.links.new(prev, n.inputs["Geometry"]); prev = n.outputs["Geometry"]
    tree.links.new(prev, gout.inputs[0])
    mod = obj.modifiers.new("HairTexture", "NODES")
    mod.node_group = tree
    return mod


def half_up_bun(scene, base_verts, mom):
    t0 = time.time()
    sc = haircut.Scalp(base_verts)
    body = Body(base_verts)
    lm = sculpt.landmarks(human.to_blender(base_verts))
    F, E = sc.lm["front_y"], sc.eye_z
    chin_z = float(lm["chin"][2])

    # ---- painted density: where hair grows at all, then which section each root belongs to
    pts, nrm = hair_mod.sample_surface(sc.verts, sc.faces, 400000, seed=1)
    flip = np.einsum("ij,ij->i", nrm, pts - sc.centre) < 0
    nrm[flip] *= -1
    def density(P):
        h, back, x = P[:, 2] - E, P[:, 1] - F, np.abs(P[:, 0])
        fl = env("HAIRLINE", 0.060) - 0.025 * np.clip(x / 0.07, 0, 1)
        w_face = sig(0.085 - back, 0.008)
        w_side = sig(0.14 - back, 0.008) * (1 - w_face)
        line = w_face * fl + w_side * (-0.005) + (1 - w_face - w_side) * env("NAPE", -0.075)
        ears = np.hypot(P[:, 1] - (F + 0.105), P[:, 2] - (E - 0.03))
        return sig(h - line, 0.004) * np.where(x > 0.055, sig(ears - 0.036, 0.004), 1.0)
    h, back, x = pts[:, 2] - E, pts[:, 1] - F, np.abs(pts[:, 0])
    # soft section borders: each root's position is jittered before it is sorted into a section, so strands of
    # neighbouring sections interleave over ~BLEND metres instead of meeting at a hard line (Nick, 14 Nov: "patches")
    jr = np.random.default_rng(7)
    B = env("BLEND", 0.012)
    hj, bj, xj = h + jr.uniform(-B, B, len(h)), back + jr.uniform(-B, B, len(h)), x + jr.uniform(-B, B, len(h))
    dens = density(pts)
    rng = np.random.default_rng(2)
    grows = rng.random(len(pts)) < dens
    bangs = (bj < env("BANG_DEPTH", 0.080)) & (xj < env("BANG_W", 0.048)) & (x > env("PART", 0.005))
    part_zone = (back < env("BANG_DEPTH", 0.080)) & (x <= env("PART", 0.005))   # the parting itself grows nothing
    # face-framing pieces: only a thin band just in front of the ear; the rest of the temple sweeps back into the bun (flow map, 14 Nov)
    pieces = ~bangs & ~part_zone & (xj > 0.045) & (bj > env("PIECE_BACK0", 0.085)) & (bj < env("PIECE_BACK1", 0.112)) & (hj < env("PIECE_TOP", 0.035))
    # the half-up line: low at the sides (just above the ears), rising to just under the bun at the back
    top_line = env("TOP_SIDE", 0.000) + (env("TOP_BACK", 0.035) - env("TOP_SIDE", 0.000)) * sig(bj - env("TOP_TURN", 0.15), 0.015)
    top = ~bangs & ~pieces & ~part_zone & (hj > top_line)
    lower = ~bangs & ~pieces & ~part_zone & ~top
    sections = {"bangs": bangs & grows, "pieces": pieces & grows, "top": top & grows, "lower": lower & grows}

    def pick(mask, count, seed):
        i = np.where(mask)[0]
        i = np.random.default_rng(seed).permutation(i)[:count]
        return pts[i], nrm[i]

    # ---- the bun's place: on the scalp, straight back from the head centre and raised
    el = np.radians(env("BUN_ELEV", 20.0))
    a = np.array([0.0, np.cos(el), np.sin(el)])
    hit, hn, _, _ = sc.bvh.ray_cast(Vector(sc.centre + a * 0.5), Vector(-a))
    hit = np.array(hit)
    R, r = env("BUN_R", 0.012), env("BUN_r", 0.017)
    bun_c = hit + a * r * 0.9
    print(f"hair: bun at {np.round(bun_c, 3)}, eye z {E:.3f}, chin z {chin_z:.3f}", flush=True)
    made = {}

    # 2 top: swept back into the bun
    roots, rn = pick(sections["top"], env("G_TOP", 320), 10)
    est = np.linalg.norm(hit - roots, axis=1) * 1.25
    front = np.clip((roots[:, 1] - F - 0.06) / -0.06 + 1.0, 0, 1)          # 1 at the front of the head
    vol = env("VOL", 0.010)
    clear_top = lambda P, s, idx=slice(None): 0.002 + vol * (0.4 + 0.6 * front[idx]) * np.sin(np.pi * np.clip(s / est[idx], 0, 1))
    g = grow(body, roots, rn, lambda P, s, idx: hit - P, lambda P, s, idx: np.linalg.norm(hit - P, axis=1) < 0.012, clear_top)
    croots, _ = pick(sections["top"], env("N_TOP", 42000), 11)
    kids = children(body, g, croots, env("CLUMP_TOP", 0.15), env("FRIZZ", 0.0009), lambda t: 0.0015 + 0.004 * np.sin(np.pi * t), 12, pull_to=hit[None, None, :])
    made["top"] = (kids, hair_material("HairTop", env("MEL_TOP", env("MEL", 0.38)), env("RED", 0.50), root=env("ROOT_TOP", 0.08)))

    # 3 lower: straight down to the collar
    roots, rn = pick(sections["lower"], env("G_LOW", 300), 20)
    end_low = chin_z - env("LOW_DROP", 0.005)
    jitter = np.random.default_rng(21).normal(0, env('LOW_RAGGED', 0.016), len(roots))
    sx = np.sign(roots[:, 0]) * np.clip(np.abs(roots[:, 0]) / 0.06, 0, 1)
    g = grow(body, roots, rn, lambda P, s, idx: np.stack([-env('LOW_IN', 0.30) * sx[idx], 0.10 * np.ones(len(idx)), -np.ones(len(idx))], 1),
             lambda P, s, idx: P[:, 2] < end_low + jitter[idx], lambda P, s, idx=None: 0.002 + env('LOW_CLEAR', 0.004) * np.clip(s / 0.15, 0, 1))
    croots, _ = pick(sections["lower"], env("N_LOW", 30000), 22)
    kids = children(body, g, croots, env("CLUMP_LOW", 0.15), env("FRIZZ", 0.0009), lambda t: 0.0015 + env('LOW_CLEAR', 0.004) * 0.8 * t, 23)
    made["lower"] = (kids, hair_material("HairLower", env("MEL_LOW", 0.42), env("RED", 0.50)))

    # 4 bangs: forward off the hairline, then falling and opening out from the part
    roots, rn = pick(sections["bangs"], env("G_BANG", 140), 30)
    sxb = np.sign(roots[:, 0])
    xr = np.clip(np.abs(roots[:, 0]) / env("BANG_W", 0.048), 0, 1)
    end_b = E + env("BANG_END0", 0.022) - env("BANG_END1", 0.035) * xr + np.random.default_rng(33).normal(0, env('BANG_RAGGED', 0.010), len(roots))
    out_b = env("BANG_OUT", 0.03)

    def bang_dir(P, s, idx):
        gfall = sig(s - env("BANG_FALL", 0.020), 0.006)[:, None]
        d1 = unit(np.stack([sxb[idx] * env('BANG_SWEEP', 0.20), -np.ones(len(idx)), 0.20 * np.ones(len(idx))], 1))
        d2 = unit(np.stack([sxb[idx] * out_b * (0.5 + xr[idx]), -0.15 * np.ones(len(idx)), -np.ones(len(idx))], 1))
        return (1 - gfall) * d1 + gfall * d2
    g = grow(body, roots, rn, bang_dir, lambda P, s, idx: (P[:, 2] < end_b[idx]) & (s > 0.04),
             lambda P, s, idx=None: 0.003 + env("BANG_CLEAR", 0.004) * np.clip(s / 0.06, 0, 1))
    q = lambda v: np.round(np.percentile(v, [10, 50, 90]), 3).tolist()
    print("bangs guides: n", len(g), "root |x|", q(np.abs(g[:, 0, 0])), "tip |x|", q(np.abs(g[:, -1, 0])),
          "root h", q(g[:, 0, 2] - E), "tip h", q(g[:, -1, 2] - E), "root back", q(g[:, 0, 1] - F), "tip back", q(g[:, -1, 1] - F),
          "len", q(np.linalg.norm(np.diff(g, axis=1), axis=2).sum(1)), flush=True)
    croots, _ = pick(sections["bangs"], env("N_BANG", 2200), 31)
    kids = children(body, g, croots, env("CLUMP_BANG", 0.30), 0.0007, lambda t: 0.002 + 0.006 * t, 32)
    cx = np.abs(croots[:, 0])
    streak = (np.abs(cx - env("STREAK_X", 0.022)) < env("STREAK_W", 0.004))
    made["bangs"] = (kids[~streak], hair_material("HairBangs", env("MEL", 0.38), env("RED", 0.50)))
    made["streaks"] = (kids[streak], hair_material("HairStreaks", env("MEL_STREAK", 0.12), 0.35, root=0.10))

    # 5 pieces: down in front of the ears to the jaw, ends flicking out
    roots, rn = pick(sections["pieces"], env("G_PIECE", 60), 40)
    sxp = np.sign(roots[:, 0])
    end_p = chin_z + env("PIECE_END", 0.012)

    def piece_dir(P, s, idx):
        flick = sig((end_p + 0.012) - P[:, 2], 0.004)[:, None]
        d = np.stack([sxp[idx] * 0.05, -0.10 * np.ones(len(idx)), -np.ones(len(idx))], 1)
        return d + flick * np.stack([sxp[idx] * env('FLICK', 0.35), 0.2 * np.ones(len(idx)), np.zeros(len(idx))], 1)
    g = grow(body, roots, rn, piece_dir, lambda P, s, idx: P[:, 2] < end_p, lambda P, s, idx=None: 0.004 + 0.006 * np.clip(s / 0.08, 0, 1))
    croots, _ = pick(sections["pieces"], env("N_PIECE", 1500), 41)
    kids = children(body, g, croots, env("CLUMP_PIECE", 0.30), 0.0007, lambda t: 0.003 + 0.005 * t, 42)
    made["pieces"] = (kids, hair_material("HairPieces", env("MEL", 0.38), env("RED", 0.50)))

    # 1 bun: strands coiled round a ring on the back of the crown
    u = unit(np.cross(a, [0.0, 0.0, 1.0]) if abs(a[2]) < 0.95 else np.cross(a, [1.0, 0.0, 0.0]))
    v = np.cross(a, u)
    nb = env("N_BUN", 7000)
    br = np.random.default_rng(50)
    tt = np.linspace(0.0, 1.0, 28)[None, :]
    th = br.uniform(0, 2 * np.pi, (nb, 1)) + 2 * np.pi * br.uniform(1.0, 1.6, (nb, 1)) * tt
    psi = br.uniform(0, 2 * np.pi, (nb, 1)) + env('BUN_TWIST', 7.0) * tt
    rm = r * np.sqrt(br.uniform(0.05, 1.0, (nb, 1)))
    rd = np.cos(th)[..., None] * u + np.sin(th)[..., None] * v
    strands = bun_c + R * rd + rm[..., None] * (np.cos(psi)[..., None] * rd + np.sin(psi)[..., None] * a)
    strands = strands + br.normal(size=strands.shape) * env('BUN_FRIZZ', 0.0012) * (0.3 + tt[..., None])
    made["bun"] = (strands, hair_material("HairBun", env("MEL_BUN", 0.66), env("RED", 0.50), root=0.0))

    if env("CAP", 1):
        cen = np.array([sc.verts[list(f)].mean(axis=0) for f in sc.faces])
        keep = [f for f, d in zip(sc.faces, density(cen)) if d > env("CAP_MIN", 0.6)]
        me = bpy.data.meshes.new("HairCap")
        me.from_pydata([tuple(v) for v in sc.verts], [], [tuple(f) for f in keep])
        me.update(); me.shade_smooth()
        me.materials.append(materials.plain("HairCap", tuple(float(c) for c in os.environ.get("CAP_RGB", "0.30,0.16,0.06").split(",")), 0.7))
        cap = bpy.data.objects.new("HairCap", me); scene.collection.objects.link(cap)
        disp = cap.modifiers.new("Lift", "DISPLACE"); disp.mid_level = 0.0; disp.strength = 0.0008 * body.sign
        _rig.parent_to_bone(cap, mom, "head")
    objs = {}
    for name, (s, mat) in made.items():
        objs[name] = build(scene, mom, f"Hair_{name}", s, mat, env("HAIR_RADIUS", 0.00006))
        if env("NODES", 1):                               # off switch: NODES=0 renders the plain strands
            add_texture(objs[name], name)
    scene.cycles_curves.shape = "THICK"
    print("hair:", {k: len(v[0]) for k, v in made.items()}, f"{time.time() - t0:.0f} s", flush=True)
    return objs
