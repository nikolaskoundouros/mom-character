"""Pass-through event logger (cursor investigation, 15 Nov 2026). MODE="start" installs a modal operator that logs every event
(type, value, x, y, time) to bpy.app.driver_namespace['evlog'] and passes it on; MODE="dump" prints a summary; MODE="stop" ends it."""
import bpy, time
NS = bpy.app.driver_namespace
MODE = globals().get("MODE", "dump")
class WM_OT_evlog(bpy.types.Operator):
    bl_idname = "wm.evlog_cursor"; bl_label = "evlog"
    def modal(self, context, event):
        if NS.get("evlog_stop"):
            return {"CANCELLED"}
        NS.setdefault("evlog", []).append((round(time.time(), 3), event.type, event.value, event.mouse_x, event.mouse_y, event.is_repeat))
        return {"PASS_THROUGH"}
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self); return {"RUNNING_MODAL"}
if MODE == "start":
    try: bpy.utils.register_class(WM_OT_evlog)
    except Exception as e: print("reg", e)
    NS["evlog_stop"] = False; NS["evlog"] = []
    W = bpy.context.window_manager.windows[0]; A = next(a for a in W.screen.areas if a.type == "VIEW_3D"); R = next(r for r in A.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=W, area=A, region=R):
        print("start", bpy.ops.wm.evlog_cursor("INVOKE_DEFAULT"))
elif MODE == "stop":
    NS["evlog_stop"] = True; print("stop requested")
else:
    L = NS.get("evlog", []); print("events", len(L))
    from collections import Counter
    print(Counter((e[1], e[2]) for e in L).most_common(12))
    print(L[:6], L[-6:])
