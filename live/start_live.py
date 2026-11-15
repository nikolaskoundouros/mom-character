# GUI Blender on the pod: install and enable the MCP for Blender add-on, start its server on 127.0.0.1:9876.
import os, shutil, addon_utils, bpy
here = os.path.dirname(os.path.abspath(__file__))
dst = bpy.utils.user_resource("SCRIPTS", path="addons", create=True)
shutil.copy(os.path.join(here, "blender_mcp.py"), os.path.join(dst, "blender_mcp.py"))
import sys
if dst not in sys.path:
    sys.path.append(dst)                      # the folder was created after start-up, so Blender is not scanning it yet
addon_utils.modules_refresh()
print("MCP add-on enabled:", bool(addon_utils.enable("blender_mcp", default_set=True, persistent=True)), flush=True)
# every connector command counts as use for the pod guard on the box (it stops a pod once ~/.wb_last_use is 10+ min old)
import blender_mcp, pathlib
_orig = blender_mcp.BlenderMCPServer._execute_command_internal
def _touched(self, *a, **k):
    try:
        pathlib.Path("/root/.wb_last_use").touch()
    except Exception:
        pass
    return _orig(self, *a, **k)
if not getattr(_orig, "_touches", False):
    _touched._touches = True
    blender_mcp.BlenderMCPServer._execute_command_internal = _touched
bpy.context.preferences.view.smooth_view = 0

def start():
    sc = bpy.context.scene
    if sc is None:
        return 0.5
    sc.blendermcp_auto_start_server = True
    try:
        bpy.ops.blendermcp.start_server()
    except Exception as exc:
        print("start_server:", exc, flush=True)
    print("MCP server running:", getattr(sc, "blendermcp_server_running", None), flush=True)
    return None
bpy.app.timers.register(start, first_interval=2.0)


def watchdog():
    """Restart the MCP server if it stopped (it did once after a failed long call)."""
    sc = bpy.context.scene
    server = getattr(bpy.types, "blendermcp_server", None)
    if sc is not None and (server is None or not server.running):
        try:
            import blender_mcp
            if server is None:
                server = blender_mcp.BlenderMCPServer(host="127.0.0.1", port=9876)
                bpy.types.blendermcp_server = server
            server.start()
            print("watchdog: MCP server restarted", server.running, flush=True)
        except Exception as exc:
            print("watchdog:", exc, flush=True)
    return 5.0
bpy.app.timers.register(watchdog, first_interval=10.0, persistent=True)
