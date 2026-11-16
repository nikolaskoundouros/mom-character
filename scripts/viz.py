import cv2, numpy as np, sys, os, time
S="/private/tmp/claude-501/-Users-nick/e53bbed9-cca3-49b0-bf6a-b54722760597/scratchpad"; A=f"{S}/ana"
iou=float(sys.argv[1]); label=sys.argv[2] if len(sys.argv)>2 else ""
H=f"{A}/iou_history.txt"; open(H,"a").write(f"{time.strftime('%H:%M:%S')}\t{iou:.3f}\t{label}\n")
hist=[(l.split('\t')[0],float(l.split('\t')[1]),l.split('\t')[2].strip()) for l in open(H) if float(l.split("\t")[1])>0]
ref=cv2.imread("/Users/nick/Desktop/mom-character/refs/heads/head_62.0.png"); o=cv2.imread(f"{A}/fit_side.png",cv2.IMREAD_UNCHANGED)
poly=np.array([(30,190),(55,150),(110,125),(200,112),(300,125),(345,160),(383,230),(378,285),(335,300),(285,305),(268,340),(255,400),(235,480),(195,530),(130,553),(105,500),(75,380),(65,300),(35,250)],np.int32)
pm=(cv2.imread(f"{A}/outline_side.png",0)>127).astype(np.uint8); a=o[...,3]>64
vis=(ref*0.45).astype(np.uint8); vis[a&(pm==1)]=(150,150,150); vis[a&(pm==0)]=(0,0,255); vis[(~a)&(pm==1)]=(255,128,0); cnt,_=cv2.findContours(pm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cv2.drawContours(vis,cnt,-1,(0,255,255),1)
fl=(o[...,:3]*(o[...,3:4]/255.0)).astype(np.uint8)
ov=(ref*(1-0.5*(o[...,3:4]/255.0))+o[...,:3]*0.5*(o[...,3:4]/255.0)).astype(np.uint8)
def cap(im,t): im=im.copy(); cv2.rectangle(im,(0,0),(520,28),(0,0,0),-1); cv2.putText(im,t,(8,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2); return im
top=np.hstack([cap(ref,"HER FRAME (62.0 s)"),cap(fl,"OUR HAIR, same camera"),cap(ov,"OVERLAY"),cap(vis,"red=ours extra  blue=missing")])
# score history chart
W=top.shape[1]; ch=np.full((170,W,3),24,np.uint8); n=len(hist)
cv2.putText(ch,f"IoU vs her silhouette: now {iou:.3f}   (start 0.597)   target 0.90",(10,24),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
x0,x1,y0,y1=60,W-30,50,150
cv2.line(ch,(x0,y1),(x1,y1),(90,90,90),1); cv2.line(ch,(x0,y0),(x0,y1),(90,90,90),1)
def Y(v): return int(y1-(v-0.5)/0.45*(y1-y0))
for t in (0.6,0.7,0.8,0.9): cv2.line(ch,(x0,Y(t)),(x1,Y(t)),(60,60,60),1); cv2.putText(ch,f"{t:.1f}",(20,Y(t)+5),cv2.FONT_HERSHEY_SIMPLEX,0.45,(170,170,170),1)
pts=[(int(x0+(x1-x0)*i/max(n-1,1)),Y(h[1])) for i,h in enumerate(hist)]
for i in range(1,n): cv2.line(ch,pts[i-1],pts[i],(0,255,0),2)
for p in pts: cv2.circle(ch,p,3,(0,255,0),-1)
if hist: cv2.putText(ch,hist[-1][2][:70],(x0,y1+16),cv2.FONT_HERSHEY_SIMPLEX,0.45,(200,200,200),1)
cv2.imwrite(f"{S}/snaps/latest.jpg",np.vstack([top,ch]))
