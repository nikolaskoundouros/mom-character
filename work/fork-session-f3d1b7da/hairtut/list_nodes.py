import bpy
p = "/Users/nick/funnel-env/venv/lib/python3.13/site-packages/bpy/5.3/datafiles/assets/nodes/procedural_hair_node_assets.blend"
with bpy.data.libraries.load(p) as (src, _):
    print(sorted(src.node_groups))
