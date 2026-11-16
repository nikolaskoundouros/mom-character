import bpy
hair = bpy.context.window_manager.windows[0].scene.objects["Hair_Top"]
mod = next(m for m in hair.modifiers if m.name == "Interpolate Hair Curves")
print(type(mod), [a for a in dir(mod) if not a.startswith("_")])
