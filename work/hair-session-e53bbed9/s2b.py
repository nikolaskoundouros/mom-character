import bpy
hair = bpy.context.window_manager.windows[0].scene.objects["Hair_Top"]
print("modifiers:", [(i, m.type, m.name, getattr(getattr(m, "node_group", None), "name", None)) for i, m in enumerate(hair.modifiers)])
mod = next(m for m in hair.modifiers if getattr(m, "node_group", None) and m.node_group.name.startswith("Interpolate"))
ng = mod.node_group
for it in ng.interface.items_tree:
    if getattr(it, "in_out", "") == "INPUT":
        v = getattr(it, "default_value", None)
        try:
            v = tuple(v)
        except TypeError:
            pass
        print(" IN", it.identifier, "|", it.name, "|", it.socket_type, "|", v)
try:
    print("keys:", list(mod.keys()))
except Exception as e:
    print("keys err", e)
