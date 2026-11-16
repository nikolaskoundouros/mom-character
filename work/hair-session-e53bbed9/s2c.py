import bpy
W = bpy.context.window_manager.windows[0]
hair = W.scene.objects["Hair_Top"]
mod = next(m for m in hair.modifiers if m.name == "Interpolate Hair Curves")
for k, v in (("Input_28", 0.035), ("Input_15", 3000.0), ("Input_10", 4)):
    mod[k] = v
for v in ("Poisson Disk", 1):
    try:
        mod["Socket_2"] = v
        print("distribution set with", repr(v), "->", mod["Socket_2"])
        break
    except Exception as e:
        print("menu set failed", repr(v), e)
hair.update_tag()
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ev = hair.evaluated_get(dg)
print("evaluated curves:", len(ev.data.curves), "points:", len(ev.data.points), "(guides:", len(hair.data.curves), ")")
for a in W.screen.areas:
    a.tag_redraw()
