"""Yesterday's live-only hair settings (14 Nov), written down so a fresh pod gets back to the same look.
Run inside the live pod Blender AFTER rebuild_live.py, in steps (each is one connector call, so none times out):
    STEP = "gloss";   exec(open(".../scripts/finish_hair.py").read())   # wet gloss on every hair material
    STEP = "top";     exec(...)                                           # smooth top, bangs, pieces: no frizz, tighter locks
    A, B = 1, 10;     exec(open(".../live/sim.py").read())               # gravity on the lower hair, then 11-25, 26-40
    STEP = "lower";   exec(...)                                           # convert the settled hair, add the finish chain
Settings are the last ones Nick saw (renders w3 / g11, 14 Nov evening)."""
import sys

import bpy

L = "/Users/nick/Desktop/mom-character"
if f"{L}/scripts" not in sys.path:
    sys.path.insert(0, f"{L}/scripts")
import mom_hair  # noqa: E402

W = bpy.context.window_manager.windows[0]
sc = W.scene
STEP = globals().get("STEP", "")


def node(tree, prefix):
    return next(n for n in tree.nodes if getattr(n, "node_tree", None) and n.node_tree.name.startswith(prefix))


if STEP == "gloss":
    for m in bpy.data.materials:
        hb = next((n for n in m.node_tree.nodes if n.type == "BSDF_HAIR_PRINCIPLED"), None) if m.node_tree else None
        if not hb:
            continue
        hb.inputs["Roughness"].default_value = 0.13
        hb.inputs["Radial Roughness"].default_value = 0.18
        hb.inputs["Random Roughness"].default_value = 0.12
        hb.inputs["Coat"].default_value = 0.16
        hb.inputs["IOR"].default_value = 1.6
        hb.inputs["Melanin Redness"].default_value = min(hb.inputs["Melanin Redness"].default_value, 0.45)
        mr = next((n for n in m.node_tree.nodes if n.type == "MAP_RANGE"), None)
        if mr and not m.get("lightened"):                      # lighter honey, to make up for the coat
            mr.inputs["To Min"].default_value *= 0.82
            mr.inputs["To Max"].default_value *= 0.82
            m["lightened"] = True
    print("gloss: roughness 0.13, coat 0.16, lighter honey")

elif STEP == "top":
    for name in ("Hair_top", "Hair_bangs", "Hair_streaks", "Hair_pieces"):
        o = bpy.data.objects.get(name)
        if not o or "HairTexture" not in o.modifiers:
            continue
        tree = o.modifiers["HairTexture"].node_group
        for n in tree.nodes:
            nm = getattr(getattr(n, "node_tree", None), "name", "")
            if nm.startswith("Frizz"):
                mom_hair._set(n, "Distance", 0.0)
            elif nm.startswith("Hair Curves Noise"):
                mom_hair._set(n, "Distance", 0.0006)
            elif nm.startswith("Clump"):
                mom_hair._set(n, "Factor", 0.75)
                mom_hair._set(n, "Guide Distance", 0.012)
        pr = node(tree, "Set Hair Curve Profile")
        if not tree.nodes.get("SmoothTop"):
            sm = tree.nodes.new("GeometryNodeGroup")
            sm.node_tree = mom_hair._hair_group("Smooth Hair Curves")
            sm.name = "SmoothTop"
            mom_hair._set(sm, "Amount", 1.0)
            mom_hair._set(sm, "Iterations", 12)
            mom_hair._set(sm, "Preserve Length", True)
            src = pr.inputs["Geometry"].links[0].from_socket
            tree.links.new(src, sm.inputs["Geometry"])
            tree.links.new(sm.outputs["Geometry"], pr.inputs["Geometry"])
    print("top: smoothed, no frizz, tighter locks")

elif STEP == "lower":
    em = bpy.data.objects["ScalpLower"]
    sc.frame_set(40)
    for o in sc.objects:
        o.select_set(False)
    em.select_set(True)
    W.view_layer.objects.active = em
    before = set(bpy.data.objects.keys())
    area = next(a for a in W.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=W, area=area, region=region, active_object=em, object=em):
        bpy.ops.curves.convert_from_particle_system()
    hair = next(bpy.data.objects[n] for n in set(bpy.data.objects.keys()) - before if bpy.data.objects[n].type == "CURVES")
    hair.name = "Hair_lower_groomed"
    for m in em.modifiers:
        if m.type == "PARTICLE_SYSTEM":
            m.show_render = m.show_viewport = False
    hair.data.materials.clear()
    hair.data.materials.append(bpy.data.materials["HairLowerDark"])
    body = bpy.data.objects["Mom"]
    hair.data.surface = body
    hair.data.surface_uv_map = body.data.uv_layers[0].name
    # keep ~half the strands at the sides, fewer in the middle -> Smooth -> draw the ends in -> turn them under
    # -> soft shared wave -> thick tapered strands
    t = bpy.data.node_groups.new("HairFinish_lower", "GeometryNodeTree")
    t.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    t.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, Lk = t.nodes, t.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    keep = N.new("GeometryNodeDeleteGeometry"); keep.domain = "CURVE"
    rnd = N.new("FunctionNodeRandomValue"); rnd.data_type = "BOOLEAN"
    root = N.new("GeometryNodeGroup"); root.node_tree = mom_hair._hair_group("Curve Root")
    sep = N.new("ShaderNodeSeparateXYZ")
    ab = N.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"
    mr = N.new("ShaderNodeMapRange"); mr.clamp = True
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.0, 0.06
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.6, 0.45
    Lk.new(next(o for o in root.outputs if "Position" in o.name), sep.inputs[0])
    Lk.new(sep.outputs["X"], ab.inputs[0]); Lk.new(ab.outputs[0], mr.inputs["Value"])
    Lk.new(mr.outputs["Result"], next(i for i in rnd.inputs if i.enabled and i.name == "Probability"))
    Lk.new(next(o for o in rnd.outputs if o.enabled and o.type == "BOOLEAN"), keep.inputs["Selection"])
    sm = N.new("GeometryNodeGroup"); sm.node_tree = mom_hair._hair_group("Smooth Hair Curves")
    for k, v in (("Amount", 1.0), ("Iterations", 20), ("Preserve Length", True)):
        mom_hair._set(sm, k, v)

    def ends_offset(xk=0.0, yk=0.0, zk=0.0, power=2.0, scale_by_x=False):
        sp = N.new("GeometryNodeSetPosition")
        par = N.new("GeometryNodeSplineParameter")
        pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = power
        Lk.new(par.outputs["Factor"], pw.inputs[0])
        cb = N.new("ShaderNodeCombineXYZ")
        if scale_by_x:
            pos = N.new("GeometryNodeInputPosition"); s2 = N.new("ShaderNodeSeparateXYZ")
            k = N.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = xk
            mx = N.new("ShaderNodeMath"); mx.operation = "MULTIPLY"
            Lk.new(pos.outputs[0], s2.inputs[0]); Lk.new(s2.outputs["X"], k.inputs[0])
            Lk.new(k.outputs[0], mx.inputs[0]); Lk.new(pw.outputs[0], mx.inputs[1]); Lk.new(mx.outputs[0], cb.inputs["X"])
        for axis, kk in (("Y", yk), ("Z", zk)):
            if kk:
                m = N.new("ShaderNodeMath"); m.operation = "MULTIPLY"; m.inputs[1].default_value = kk
                Lk.new(pw.outputs[0], m.inputs[0]); Lk.new(m.outputs[0], cb.inputs[axis])
        Lk.new(cb.outputs[0], sp.inputs["Offset"])
        return sp

    narrow = ends_offset(xk=-0.45, power=2.0, scale_by_x=True)        # ends drawn in to the middle
    under = ends_offset(yk=-0.035, zk=0.02, power=3.0)                 # ends turn under toward her neck
    wave = N.new("GeometryNodeGroup"); wave.node_tree = mom_hair._hair_group("Hair Curves Noise")
    for k, v in (("Distance", 0.007), ("Scale", 7.0), ("Shape", 0.8), ("Scale along Curve", 1.0),
                 ("Offset per Curve", 0.0), ("Preserve Length", True), ("Factor", 1.0)):
        mom_hair._set(wave, k, v)
    pr = N.new("GeometryNodeGroup"); pr.node_tree = mom_hair._hair_group("Set Hair Curve Profile")
    mom_hair._set(pr, "Radius", 0.00028)
    mom_hair._set(pr, "Shape", 0.5)
    chain = [gi, keep, sm, narrow, under, wave, pr, go]
    for a, b in zip(chain, chain[1:]):
        Lk.new(a.outputs[0], b.inputs[0])
    mod = hair.modifiers.new("HairFinish", "NODES")
    mod.node_group = t
    print("lower: converted", len(hair.data.curves), "strands; finish chain keep -> smooth -> narrow -> under -> wave -> profile")
else:
    print("set STEP to gloss, top or lower")
