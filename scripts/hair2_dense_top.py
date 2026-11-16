"""Hair from scratch, step 2 (15 Nov 2026): dense Top hair from the shaped guides, built in DATA.
Why not the Interpolate Hair Curves modifier: in this Blender 5.2.2 build the modifier inputs could not be set from
Python (properties.inputs is empty, see results.tsv), so the plan switched to this. Children follow their guide, clump a
little toward it near the tip, and are mirrored left to right. Run live after hair2_shape_top.py.
Knobs (my plan, tuned and recorded): N_PER (children per guide), SPREAD (root scatter radius), FRIZZ."""
import math
import random

import bpy
import numpy as np
from mathutils import Vector

N_PER, SPREAD, FRIZZ, RADIUS = 1500, 0.080, 0.0007, 0.00011
HAIRLINE_Z, BACK_Y = 1.565, 0.040                    # my plan: hairline / temple height and back limit of the Top section
MEL, RED, ROUGH, ASPECT = 0.46, 0.60, 0.30, 0.75
W = bpy.context.window_manager.windows[0]
sc = W.scene
hair, mom = sc.objects["Hair_Top"], sc.objects["Mom"]
for m in list(hair.modifiers):
    if m.name == "Interpolate Hair Curves":
        hair.modifiers.remove(m)
n = len(hair.data.curves); per = len(hair.data.points) // n
buf = [0.0] * (3 * len(hair.data.points))
hair.data.attributes["position"].data.foreach_get("vector", buf)
G = np.array(buf, dtype=np.float64).reshape(n, per, 3)
G = np.concatenate([G, G * np.array([-1.0, 1.0, 1.0])])           # mirror X
inv = mom.matrix_world.inverted()
d_down = inv.to_3x3() @ Vector((0, 0, -1))


def scalp_z(x, y, fallback):
    ok, loc, nrm, i = mom.ray_cast(inv @ Vector((x, y, 1.9)), d_down)
    return (mom.matrix_world @ loc).z if ok else fallback


rng = random.Random(7)
t = np.linspace(0.0, 1.0, per)[:, None]
out = []
for g in G:
    made = 0
    while made < N_PER:
        r = SPREAD * math.sqrt(rng.random()); a = rng.random() * 2 * math.pi
        dx, dy = r * math.cos(a), r * math.sin(a)
        zr = scalp_z(g[0, 0] + dx, g[0, 1] + dy, 0.0)
        if zr < HAIRLINE_Z or g[0, 1] + dy > BACK_Y:        # roots only above the hairline and temples, not on her face
            continue
        made += 1
        rz = zr - g[0, 2]
        off = np.array([dx, dy, rz])[None, :] * np.concatenate([np.ones((per, 1)), np.ones((per, 1))], axis=1)[:, :1]
        shrink = (1.0 - 0.45 * t)                                    # clump toward the guide near the tip
        zdec = (1.0 - t)                                             # root on the scalp, tip free
        child = g + np.concatenate([np.array([dx, dy])[None, :] * shrink, rz * zdec], axis=1)
        child += np.random.default_rng(rng.randrange(1 << 30)).normal(0, FRIZZ, child.shape) * t
        out.append(child)
C = np.array(out)                                                    # (N, per, 3)
N = len(C)
old = bpy.data.objects.get("Hair_Top_dense")
if old:
    bpy.data.objects.remove(old, do_unlink=True)
cd = bpy.data.hair_curves.new("Hair_Top_dense")
cd.add_curves([per] * N)
cd.attributes["position"].data.foreach_set("vector", C.reshape(-1).astype(np.float32))
rad = cd.attributes.get("radius") or cd.attributes.new("radius", "FLOAT", "POINT")
rad.data.foreach_set("value", np.full(N * per, RADIUS, dtype=np.float32))
cd.surface = mom
cd.surface_uv_map = "UVMap"
ob = bpy.data.objects.new("Hair_Top_dense", cd)
sc.collection.objects.link(ob)
ob.parent = mom
mat = bpy.data.materials.get("Hair2_Top") or bpy.data.materials.new("Hair2_Top")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
out_n = nt.nodes.new("ShaderNodeOutputMaterial")
hb = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
hb.parametrization = "MELANIN"
try:
    hb.model = "HUANG"
except TypeError as e:
    print("Huang not set:", e)
hb.inputs["Melanin"].default_value = MEL
hb.inputs["Melanin Redness"].default_value = RED
hb.inputs["Roughness"].default_value = ROUGH
if "Aspect Ratio" in hb.inputs:
    hb.inputs["Aspect Ratio"].default_value = ASPECT
if "Coat" in hb.inputs:
    hb.inputs["Coat"].default_value = 0.0
nt.links.new(hb.outputs[0], out_n.inputs["Surface"])
cd.materials.append(mat)
hair.hide_viewport = False
print("dense hair:", N, "curves,", per, "points each; model", hb.model, "melanin", MEL, "roughness", ROUGH)
