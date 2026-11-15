#!/bin/bash
# Run ON THE BOX. Rents a workbench GPU pod if none is up (costs money: ask Nick first), copies the projects to it,
# starts Blender on the pod's RTX with a virtual screen + the MCP add-on, and tunnels port 9876 from the box to it,
# so the box's Claude session drives the live Blender. Nothing here depends on the Mac.
#   live/pod_live.sh          set up (or reconnect to) the live Blender
#   live/pod_live.sh tunnel   only reopen the tunnel
# The box's pod-guard.timer stops the pod after 10 idle minutes; every connector command counts as use.
set -u
P="$(cd "$(dirname "$0")/.." && pwd)"
WB="$HOME/Desktop/render-desk/bin/workbench"
STATE="$HOME/.local/share/render-desk/workbench.json"

tunnel() {
  read -r H PORT U < <(python3 -c "import json;print(*json.load(open('$STATE'))['target'])")
  pkill -f "L 127.0.0.1:9876:127.0.0.1:9876" 2>/dev/null
  ssh -f -N -i "$HOME/.ssh/id_ed25519" -p "$PORT" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null \
      -o LogLevel=ERROR -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
      -L 127.0.0.1:9876:127.0.0.1:9876 "$U@$H" && echo "tunnel: box 127.0.0.1:9876 -> pod Blender"
}
[ "${1:-}" = tunnel ] && { tunnel; exit; }

"$WB" status | grep -q "WB up" || "$WB" up || exit 1
"$WB" push "$HOME/Desktop/blender-funnel" >/dev/null && "$WB" push "$P" >/dev/null && echo "projects copied to the pod"
"$WB" run '
  command -v xvfb-run >/dev/null && command -v xdotool >/dev/null || (apt-get update -qq && DEBIAN_FRONTEND=noninteractive \
    apt-get install -y -qq xvfb xdotool libxkbcommon0 libxi6 libxrender1 libsm6 >/dev/null 2>&1)
  dpkg -s virtualgl >/dev/null 2>&1 || (cd /root && wget -q https://github.com/VirtualGL/virtualgl/releases/download/3.1.5/virtualgl_3.1.5_amd64.deb \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ./virtualgl_3.1.5_amd64.deb >/dev/null 2>&1)
  mkdir -p /root/live_snaps; touch /root/.wb_last_use
  if ss -ltn | grep -q 9876; then echo "live Blender already running"; else
    cd '"$P"'/live && nohup setsid xvfb-run --auto-servernum -s "-screen 0 1920x1080x24 +extension GLX" \
      /opt/VirtualGL/bin/vglrun -d egl $BLENDER --python start_live.py > /root/live_gui.log 2>&1 < /dev/null &
    for i in $(seq 1 30); do ss -ltn | grep -q 9876 && break; sleep 2; done
    ss -ltn | grep -q 9876 && echo "live Blender up (GPU-drawn, MCP on 9876)" || { echo "live Blender did not start"; tail -20 /root/live_gui.log; exit 1; }
  fi'
tunnel
