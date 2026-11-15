#!/bin/bash
# Run ON THE BOX after live/pod_live.sh: rebuilds her in the live Blender with the last settings Nick saw, then renders
# the four head views and the reference comparison. Usage: live/rebuild_all.sh [tag]   (default tag: base)
set -e
P="$(cd "$(dirname "$0")/.." && pwd)"; TAG="${1:-base}"
b() { python3 "$P/live/bcall.py" --timeout 900 "$1" | tail -2; }
b "exec(open('$P/scripts/rebuild_live.py').read())"
b "STEP='gloss'; exec(open('$P/scripts/finish_hair.py').read())"
b "STEP='top'; exec(open('$P/scripts/finish_hair.py').read())"
for r in 1,10 11,25 26,40; do b "A,B=$r; exec(open('$P/live/sim.py').read())"; done
b "STEP='lower'; exec(open('$P/scripts/finish_hair.py').read())"
b "exec(open('$P/live/live_tools.py').read()); print(bpy.app.driver_namespace['shoot']('$TAG', samples=64))"
"$P/live/pullcmp.sh" "$TAG"
