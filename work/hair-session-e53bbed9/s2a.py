import bpy
W = bpy.context.window_manager.windows[0]
sc = W.scene
AREA = next(a for a in W.screen.areas if a.type == "VIEW_3D")
REGION = next(r for r in AREA.regions if r.type == "WINDOW")
hair = sc.objects["Hair_Top"]
kw = dict(window=W, area=AREA, region=REGION, active_object=hair, object=hair)
with bpy.context.temp_override(**kw):
    if hair.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    r = bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_library_identifier="",
        relative_asset_identifier="nodes/procedural_hair_node_assets.blend/NodeTree/Interpolate Hair Curves")
print("add modifier:", r, [(m.type, m.name) for m in hair.modifiers])
mod = hair.modifiers[-1]
ng = mod.node_group
print("node group:", ng.name)
for it in ng.interface.items_tree:
    if getattr(it, "in_out", "") == "INPUT":
        print(" IN", it.identifier, "|", it.name, "|", it.socket_type, "|", getattr(it, "default_value", None), "|", getattr(it, "min_value", None), getattr(it, "max_value", None))
print("current values:", {k: mod[k] for k in mod.keys() if k.startswith("Socket_")})
