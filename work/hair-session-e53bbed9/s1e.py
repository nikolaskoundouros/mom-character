import bpy
W = bpy.context.window_manager.windows[0]
sc = W.scene
hair = sc.objects["Hair_Top"]
n = len(hair.data.curves)
try:
    hair.data.remove_curves(indices=list(range(n)))
    print("removed", n, "now", len(hair.data.curves))
except Exception as e:
    print("remove_curves failed:", e)
ts = bpy.context.tool_settings
ups = ts.curves_sculpt.unified_paint_settings
print("unified size before:", ups.size, "use_unified_size", ups.use_unified_size)
ups.size = 14
b = ts.curves_sculpt.brush
b.size = 14
print("brush size:", b.size, "unified:", ups.size, "count:", b.curves_sculpt_settings.add_amount,
      "len", b.curves_sculpt_settings.curve_length, "pts", b.curves_sculpt_settings.points_per_curve)
