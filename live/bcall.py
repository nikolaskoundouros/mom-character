"""Send Python to the live pod Blender through the box tunnel (127.0.0.1:9876), print what it prints.
Usage (on the box): python3 live/bcall.py 'code'   or   python3 live/bcall.py -f file.py   [--timeout 600]
Same socket the MCP connector uses; for scripted steps when no Claude session is needed."""
import json, socket, sys
args = sys.argv[1:]
timeout = 600
if "--timeout" in args:
    i = args.index("--timeout"); timeout = float(args[i + 1]); del args[i:i + 2]
code = open(args[1]).read() if args[0] == "-f" else args[0]
s = socket.create_connection(("127.0.0.1", 9876), timeout=timeout)
s.sendall(json.dumps({"type": "execute_code", "params": {"code": code}}).encode())
buf = b""
while True:
    chunk = s.recv(65536)
    if not chunk:
        break
    buf += chunk
    try:
        reply = json.loads(buf.decode()); break
    except ValueError:
        continue
s.close()
r = reply.get("result", reply)
print(r.get("result", r) if isinstance(r, dict) else r)
sys.exit(0 if reply.get("status") == "success" else 1)
