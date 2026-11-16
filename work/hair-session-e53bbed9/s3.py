import bpy
W = bpy.context.window_manager.windows[0]
hair = W.scene.objects["Hair_Top"]
mod = next(m for m in hair.modifiers if m.name == "Interpolate Hair Curves")
inp = mod.properties.inputs
items = list(inp) if hasattr(inp, "__iter__") else []
print("n inputs", len(items), [(getattr(i, "name", None), [a for a in dir(i) if not a.startswith("_")][:12]) for i in items[:2]])
vals = {"Density": 300000.0, "Distance to Guides": 0.035, "Interpolation Guides": 4}
ok = 0
for it in items:
    nm = getattr(it, "name", None)
    if nm in vals:
        for attr in ("value", "default_value"):
            try:
                setattr(it, attr, vals[nm]); ok += 1; print("set", nm, "via", attr); break
            except Exception as e:
                print("fail", nm, attr, str(e)[:80])
print("set", ok, "of", len(vals))
hair.update_tag(); bpy.context.view_layer.update()
ev = hair.evaluated_get(bpy.context.evaluated_depsgraph_get())
print("evaluated curves:", len(ev.data.curves), "guides:", len(hair.data.curves))
