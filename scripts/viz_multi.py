import cv2, numpy as np, sys, time, re
S="/private/tmp/claude-501/-Users-nick/e53bbed9-cca3-49b0-bf6a-b54722760597/scratchpad"; A=f"{S}/ana"; R="/Users/nick/Desktop/mom-character/refs/heads"
mean=float(sys.argv[1]); label=sys.argv[2]; per=sys.argv[3] if len(sys.argv)>3 else ""
H=f"{A}/iou_multi.txt"; open(H,"a").write(f"{time.strftime('%H:%M:%S')}\t{mean:.3f}\t{label}\t{per}\n")
hist=[l.rstrip("\n").split("\t") for l in open(H)]
def row(v,img):
    ref=cv2.imread(f"{R}/{img}"); o=cv2.imread(f"{A}/fit_{v}.png",cv2.IMREAD_UNCHANGED); m=cv2.imread(f"{A}/outline_{v}.png",0)>127
    a=o[...,3]>64; 
    if v=="q34": m=m.copy(); a=a.copy(); m[420:]=False; a[420:]=False
    vis=(ref*0.45).astype(np.uint8); vis[a&m]=(150,150,150); vis[a&~m]=(0,0,255); vis[(~a)&m]=(255,128,0)
    al=o[...,3:4]/255.0; ov=(ref*(1-0.5*al)+o[...,:3]*0.5*al).astype(np.uint8); fl=(o[...,:3]*al).astype(np.uint8)
    def cap(im,t): im=im.copy(); cv2.rectangle(im,(0,0),(520,26),(0,0,0),-1); cv2.putText(im,t,(8,19),cv2.FONT_HERSHEY_SIMPLEX,0.55,(0,255,255),2); return im
    return np.hstack([cap(ref,f"HER {v}"),cap(fl,"OUR HAIR, same camera"),cap(ov,"OVERLAY"),cap(vis,"red=extra blue=missing")])
img=np.vstack([row("side","head_62.0.png"),row("q34","head_18.0.png")])
W=img.shape[1]; ch=np.full((150,W,3),24,np.uint8)
cv2.putText(ch,f"MEAN IoU over side + 3/4: now {mean:.3f}   {per}   (target 0.90)",(10,24),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
x0,x1,y0,y1=60,W-30,45,130
def Y(v): return int(y1-(v-0.5)/0.45*(y1-y0))
for t in (0.6,0.7,0.8,0.9): cv2.line(ch,(x0,Y(t)),(x1,Y(t)),(60,60,60),1); cv2.putText(ch,f"{t:.1f}",(20,Y(t)+5),cv2.FONT_HERSHEY_SIMPLEX,0.45,(170,170,170),1)
vals=[float(h[1]) for h in hist]; n=len(vals); pts=[(int(x0+(x1-x0)*i/max(n-1,1)),Y(v)) for i,v in enumerate(vals)]
for i in range(1,n): cv2.line(ch,pts[i-1],pts[i],(0,255,0),2)
for p in pts: cv2.circle(ch,p,3,(0,255,0),-1)
cv2.putText(ch,hist[-1][2][:90],(x0,y1+14),cv2.FONT_HERSHEY_SIMPLEX,0.45,(200,200,200),1)
cv2.imwrite(f"{S}/snaps/latest.jpg",np.vstack([img,ch]))
