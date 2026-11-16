# Runs inside GUI Blender at startup: use only the new add-on module, start its server.
import addon_utils, bpy
try:
    addon_utils.disable("addon", default_set=True)          # the old copy of the same add-on
except Exception as exc:
    print("disable old:", exc)
mod = addon_utils.enable("blender_mcp", default_set=True, persistent=True)
print("MCP add-on enabled:", bool(mod))
bpy.ops.wm.save_userpref()

def start():
    sc = bpy.context.scene
    if sc is None:
        return 0.5
    sc.blendermcp_auto_start_server = True
    try:
        bpy.ops.blendermcp.start_server()
    except Exception as exc:
        print("start_server:", exc)
    print("MCP server running:", getattr(sc, "blendermcp_server_running", None))
    return None
bpy.app.timers.register(start, first_interval=1.5)
