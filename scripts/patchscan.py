import cv2, numpy as np, sys
D="/private/tmp/claude-501/-Users-nick/e53bbed9-cca3-49b0-bf6a-b54722760597/scratchpad/scan"
def mag(im):
    f=im.astype(np.float32)/255.0; b,g,r=f[...,0],f[...,1],f[...,2]
    return (r>0.45)&(b>0.40)&(g<0.55*np.minimum(r,b))
P,S=40,20
out=[]
for k in ("top","crown","back","ear","front"):
    n=cv2.imread(f"{D}/scan_n_{k}.png"); L=mag(cv2.imread(f"{D}/scan_lock_{k}.png")); K=mag(cv2.imread(f"{D}/scan_skin_{k}.png"))
    h,w=L.shape; rows=int(h*0.80)
    bg=np.median(n[:20,:20].reshape(-1,3),axis=0); fg=(np.abs(n.astype(np.float32)-bg).max(axis=2)>20)
    fg[rows:]=False
    nf=max(1,int(fg.sum()))
    lockpx=int((L&fg).sum()); skinpx=int((K&fg).sum())
    # sliding window = a "convolution" with a PxP box kernel over the masks
    k1=np.ones((P,P),np.float32)/(P*P)
    Lm=cv2.filter2D(L.astype(np.float32),-1,k1)[P//2::S,P//2::S]; Km=cv2.filter2D(K.astype(np.float32),-1,k1)[P//2::S,P//2::S]
    fm=cv2.filter2D(fg.astype(np.float32),-1,k1)[P//2::S,P//2::S]
    # only patches that are mostly hair/foreground
    valid=fm>0.6
    lockp=np.where(valid,Lm,0); skinp=np.where(valid,Km,0)
    def worst(m,name,n=5):
        idx=np.dstack(np.unravel_index(np.argsort(-m.ravel()),m.shape))[0][:n]
        return [(name,int(j*S+P//2),int(i*S+P//2),round(float(m[i,j]),2)) for i,j in idx if m[i,j]>0.02]
    ww=worst(lockp,"ribbon")+worst(skinp,"skin")
    out.append((k,lockpx,skinpx,nf,(lockp>0.25).sum(),(skinp>0.10).sum(),ww))
    vis=n.copy(); vis[L&fg]=(0,255,255); vis[K&fg]=(255,255,0)
    for nme,x,y,v in ww:
        cv2.rectangle(vis,(x-P//2,y-P//2),(x+P//2,y+P//2),(0,0,255) if nme=="ribbon" else (255,0,0),2)
    cv2.imwrite(f"{D}/heat_{k}.jpg",vis)
print("view   ribbon%   skin%   bad_ribbon_patches  bad_skin_patches   worst patches (type,x,y,fraction)")
for k,lp,sp,nf,bl,bs,ww in out:
    print(f"{k:6s} {100*lp/nf:7.2f} {100*sp/nf:7.2f}   {bl:10d} {bs:16d}   {ww[:4]}")
