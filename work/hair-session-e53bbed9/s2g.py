import bpy
hair = bpy.context.window_manager.windows[0].scene.objects["Hair_Top"]
mod = next(m for m in hair.modifiers if m.name == "Interpolate Hair Curves")
pr = mod.properties
print(type(pr), [a for a in dir(pr) if not a.startswith("_")][:40])
try:
    print("density via getitem:", pr["Input_15"])
except Exception as e:
    print("getitem err", e)
for name in ("Input_15", "Density"):
    try:
        print(name, "via attr:", getattr(pr, name))
    except Exception as e:
        print(name, "attr err", e)
