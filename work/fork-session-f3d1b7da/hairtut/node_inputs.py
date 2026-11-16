import bpy
p = "/Users/nick/funnel-env/venv/lib/python3.13/site-packages/bpy/5.3/datafiles/assets/nodes/procedural_hair_node_assets.blend"
want = ["Clump Hair Curves", "Frizz Hair Curves", "Hair Curves Noise", "Set Hair Curve Profile", "Curl Hair Curves", "Smooth Hair Curves", "Duplicate Hair Curves", "Create Guide Index Map", "Interpolate Hair Curves"]
with bpy.data.libraries.load(p) as (src, dst):
    dst.node_groups = [n for n in src.node_groups if n in want]
for ng in bpy.data.node_groups:
    if ng.name not in want: continue
    ins = [(s.name, s.socket_type.replace("NodeSocket", ""), getattr(s, "default_value", None) if not hasattr(getattr(s, "default_value", None), "__len__") else tuple(s.default_value)) for s in ng.interface.items_tree if getattr(s, "in_out", "") == "INPUT"]
    outs = [s.name for s in ng.interface.items_tree if getattr(s, "in_out", "") == "OUTPUT"]
    print("##", ng.name, "| out:", outs)
    for i in ins: print("   ", i)
