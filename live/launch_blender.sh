#!/bin/bash
# Runs ON THE POD: GUI Blender on the RTX (VirtualGL EGL) with a virtual screen and the MCP add-on.
# Fully detached (all fds closed) so the ssh session that started it can end.
exec </dev/null >/root/live_gui.log 2>&1
cd "$(dirname "$0")"
exec xvfb-run --auto-servernum -s "-screen 0 1920x1080x24 +extension GLX" \
     /opt/VirtualGL/bin/vglrun -d egl "$BLENDER" --python start_live.py
