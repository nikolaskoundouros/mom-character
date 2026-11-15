# Step the gravity simulation from frame A to frame B (globals A, B), stopping early if Blender's memory runs away.
import bpy, time
def rss_gb():
    for line in open("/proc/self/status"):
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 1e6
sc = bpy.context.window_manager.windows[0].scene
t = time.time(); f = A
for f in range(A, B + 1):
    sc.frame_set(f)
    if rss_gb() > 12.0:
        print(f"STOPPED at frame {f}: memory {rss_gb():.1f} GB (simulation unstable)")
        break
print(f"frames {A}-{f} in {time.time() - t:.1f} s; memory {rss_gb():.1f} GB")
