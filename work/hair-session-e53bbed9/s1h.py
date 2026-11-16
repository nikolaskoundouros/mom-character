import bpy
from mathutils import Vector
h = bpy.context.window_manager.windows[0].scene.objects["Hair_Top"]
n = len(h.data.curves); per = len(h.data.points) // n
buf = [0.0] * (3 * len(h.data.points)); h.data.attributes["position"].data.foreach_get("vector", buf)
for c in range(n):
    r = Vector(buf[3 * c * per:3 * c * per + 3]); t = Vector(buf[3 * (c * per + per - 1):3 * (c * per + per - 1) + 3])
    print(c, tuple(round(v, 3) for v in r), tuple(round(v, 3) for v in t))
print("mode", h.mode, "brush", bpy.context.tool_settings.curves_sculpt.brush.name, bpy.context.tool_settings.curves_sculpt.brush.falloff_shape)
for a in bpy.context.window_manager.windows[0].screen.areas:
    a.tag_redraw()
