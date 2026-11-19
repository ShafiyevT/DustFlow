import sys, json, pickle, datetime as dt, numpy as np, pandas as pd, rasterio, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as md
from matplotlib.patches import FancyArrowPatch, Rectangle
sys.path.insert(0,'.')
from dustflow import emission as E
plt.rcParams.update({"font.family":"Liberation Sans","font.size":8.5,"axes.titlesize":8.5,"axes.labelsize":8.5,
                     "legend.fontsize":7.5,"xtick.labelsize":7.5,"ytick.labelsize":7.5,"savefig.dpi":600,"axes.linewidth":0.7})
OUT="/home/claude/cmes/fig/"; W=6.5
def lab(ax,s): ax.text(-0.02,1.03,s,transform=ax.transAxes,fontsize=10,fontweight="bold",va="bottom",ha="right")
def save(fig,n): fig.savefig(OUT+f"Fig{n}.png",dpi=300,bbox_inches="tight",facecolor="white"); fig.savefig(OUT+f"Fig{n}.tif",dpi=600,bbox_inches="tight",facecolor="white",pil_kwargs={"compression":"tiff_lzw"}); plt.close(fig)
CH=[0.2e-6,2.5e-6,10e-6,20e-6,50e-6,100e-6]; RHO=[1500,2000,2200,2400,2600]; MU=1.81e-5; G=9.81
# ---------- Fig 1: schematic ----------
fig,ax=plt.subplots(figsize=(W,3.1)); x=np.linspace(0,10,400); h=0.55*np.exp(-((x-6.5)/1.1)**2)+0.25*np.exp(-((x-2.5)/0.9)**2)
ax.fill_between(x,-0.35,h,color="#c8b28a"); ax.plot(x,h,color="#6d5a3a",lw=1.2)
for s_ in [0.5,1.1,1.8,2.6,3.3]: ax.plot(x,h+(4-h)*s_/4.0,color="#9aa6b2",lw=0.6,ls="--")
ax.plot([0,10],[4,4],color="k",lw=1); ax.plot([0,0],[h[0],4],color="k",lw=1); ax.plot([10,10],[h[-1],4],color="k",lw=1)
for yy in [1.3,2.2,3.1]: ax.add_patch(FancyArrowPatch((0.3,yy),(1.5,yy),arrowstyle="-|>",mutation_scale=9,color="#1f4e79",lw=1.2))
ax.text(0.3,3.45,"Wind U(x, y, z, t)",color="#1f4e79",fontsize=8)
for xs in [3.8,4.6,8.3]:
    i=np.argmin(abs(x-xs)); ax.add_patch(FancyArrowPatch((xs,h[i]+0.02),(xs,h[i]+0.75),arrowstyle="-|>",mutation_scale=8,color="#b03a2e",lw=1.2))
    ax.add_patch(FancyArrowPatch((xs+0.22,h[i]+0.7),(xs+0.22,h[i]+0.05),arrowstyle="-|>",mutation_scale=8,color="#2e7d32",lw=1.0))
ax.text(2.2,0.95,r"Emission $F_i$",color="#b03a2e",fontsize=8); ax.text(5.05,1.3,r"Dry deposition $v_{d,i}C_i$",color="#2e7d32",fontsize=8)
ax.text(5.0,-0.25,r"Surface $z=h(x,y)$:   $K_z\,\partial C_i/\partial z=-F_i+v_{d,i}\,C_i$",fontsize=8,ha="center")
ax.text(9.85,2.55,"Lateral and top boundaries:\n"+r"$K\,\partial C_i/\partial n=\gamma_i\,(C_i-C_i^{\mathrm{bg}})$",fontsize=7.8,ha="right",va="center",bbox=dict(fc="white",ec="none",alpha=0.9,pad=1))
ax.text(5.0,4.1,r"Top $z=H$",fontsize=7.8,ha="center"); ax.text(9.85,3.75,r"$\zeta$ = const (terrain-following levels)",color="#6b7785",fontsize=7,ha="right")
ax.set_xlim(-0.1,10.1); ax.set_ylim(-0.4,4.4); ax.axis("off")
save(fig,1)
# ---------- Fig 2: threshold and corrections ----------
fig,axs=plt.subplots(1,3,figsize=(W,2.2)); d=np.logspace(-6,-3,300)
a=axs[0]; ut=E.kritik_tezlik(d); a.semilogx(d*1e6,ut,color="k",lw=1.3); i=np.argmin(ut); a.plot(d[i]*1e6,ut[i],"o",ms=4,color="#b03a2e")
a.annotate(f"minimum\n{d[i]*1e6:.0f} µm, {ut[i]:.2f} m/s",(d[i]*1e6,ut[i]),(150,0.75),fontsize=7,arrowprops=dict(arrowstyle="->",lw=0.6))
a.set_xlabel("Particle diameter (µm)"); a.set_ylabel(r"$u_{*t}^{0}$ (m/s)"); a.set_ylim(0,1.3); lab(a,"A")
a=axs[1]; w=np.linspace(0,20,300)
for m,c in [(0.05,"#1f4e79"),(0.10,"#2e7d32"),(0.20,"#b03a2e")]:
    a.plot(w,E.namlik_tuzatmasi(w,np.full_like(w,m)),color=c,lw=1.2,label=f"clay {m:.2f}")
a.set_xlabel("Gravimetric soil moisture (%)"); a.set_ylabel(r"$f_w$"); a.legend(frameon=False); lab(a,"B")
a=axs[2]; lam=np.linspace(0,0.1,200); a.plot(lam,E.qoplam_tuzatmasi(lam),color="k",lw=1.3)
a.set_xlabel(r"Roughness density $\lambda$"); a.set_ylabel(r"$R_\lambda$"); lab(a,"C")
plt.tight_layout(w_pad=1.2); save(fig,2)
# ---------- Fig 3: emission flux ----------
fig,axs=plt.subplots(1,2,figsize=(W,2.35)); us=np.linspace(0.05,1.2,400)
a=axs[0]
for ut,c in [(0.22,"#1f4e79"),(0.30,"#2e7d32"),(0.45,"#e67e22"),(0.60,"#b03a2e")]:
    Q=E.gorizontal_oqim(us,np.full_like(us,ut)); F=E.vertikal_oqim(Q,np.full_like(us,0.05),1.0)
    a.semilogy(us,np.where(F>0,F,np.nan),color=c,lw=1.2,label=rf"$u_{{*t}}^{{\,\mathrm{{eff}}}}$ = {ut:.2f} m/s")
a.set_xlabel(r"Friction velocity $u_*$ (m/s)"); a.set_ylabel(r"Vertical dust flux $F$ (kg m$^{-2}$ s$^{-1}$)"); a.set_ylim(1e-9,1e-4); a.legend(frameon=False,loc="lower right"); lab(a,"A")
a=axs[1]; m=np.linspace(0,0.35,200); a.semilogy(m*100,E.sandblast_koeffitsiyenti(m),color="k",lw=1.3)
a.axvline(20,ls=":",color="#555",lw=0.8); a.text(21,2e-5,"cap at 20%",fontsize=7,color="#555")
a.set_xlabel("Clay content (%)"); a.set_ylabel(r"$\alpha=F/Q$ (m$^{-1}$)"); lab(a,"B")
plt.tight_layout(w_pad=1.5); save(fig,3)
# ---------- Fig 4: fractions ----------
p=E.fraksiya_ulushlari(CH); dbar=np.sqrt(np.array(CH[:-1])*np.array(CH[1:])); wg=np.array(RHO)*G*dbar**2/(18*MU)
fig,axs=plt.subplots(1,2,figsize=(W,2.35))
a=axs[0]; dd=np.logspace(np.log10(0.1e-6),np.log10(200e-6),400); from math import erf
pdf=np.zeros_like(dd)
for Dm,sg,wj in zip((1.5e-6,6.7e-6,45e-6),(1.7,1.6,1.5),(0.05,0.40,0.55)):
    pdf+=wj/(np.sqrt(2*np.pi)*np.log(sg))*np.exp(-(np.log(dd/Dm))**2/(2*np.log(sg)**2))
a.semilogx(dd*1e6,pdf,color="k",lw=1.2); 
for c in CH: a.axvline(c*1e6,color="#999",lw=0.6,ls="--")
for k in range(5): a.text(dbar[k]*1e6,max(pdf)*(1.02+0.09*(k%2)),f"{p[k]:.3f}",ha="center",fontsize=7,color="#b03a2e")
a.set_xlabel("Diameter (µm)"); a.set_ylabel(r"$dM/d\ln d$ (normalized)"); a.set_ylim(0,max(pdf)*1.25); a.text(0.12,max(pdf)*1.16,"Mass share:",fontsize=7,color="#b03a2e"); lab(a,"A")
a=axs[1]; a.loglog(dd*1e6,2500*G*dd**2/(18*MU)*100,color="#999",lw=0.8,label=r"Stokes, $\rho_p$ = 2500 kg/m$^3$")
a.loglog(dbar*1e6,wg*100,"o",color="#b03a2e",ms=5,label="Transport fractions")
for k in range(5): a.text(dbar[k]*1e6*1.15,wg[k]*100*0.6,f"{wg[k]*100:.3g}",fontsize=7)
a.set_xlabel("Diameter (µm)"); a.set_ylabel(r"Settling velocity $w_g$ (cm/s)"); a.legend(frameon=False,loc="upper left"); lab(a,"B")
plt.tight_layout(w_pad=1.5); save(fig,4)
json.dump(dict(p=p.tolist(),dbar=dbar.tolist(),wg=wg.tolist(),tau=(np.array(RHO)*dbar**2/(18*MU)).tolist()),open("/home/cla"+"ude/cmes/fraksiyalar.json","w"))
# ---------- Fig 5: input fields ----------
S="haqiqiy_malumot/statik/"
fig,axs=plt.subplots(2,2,figsize=(W,5.6))
for a,(f,t,cm,vmax,cb) in zip(axs.ravel(),[("relyef.tif","Terrain elevation (m)","terrain",None,"m"),("tuproq.tif","Clay fraction","YlOrBr",0.35,"–"),
                                 ("A_ef.tif",r"Erodible fraction $A_{ef}$","Reds",0.3,"–"),("z0.tif",r"Roughness length $z_0$ (m, log$_{10}$)","viridis",None,"log10 m")]):
    with rasterio.open(S+f) as s: arr=s.read(1).astype(float); b=s.bounds
    if f=="z0.tif": arr=np.log10(np.maximum(arr,1e-4))
    im=a.imshow(arr,extent=[b.left,b.right,b.bottom,b.top],cmap=cm,vmax=vmax,origin="upper",aspect=1/np.cos(np.deg2rad(40.25)))
    c=fig.colorbar(im,ax=a,fraction=0.042,pad=0.02); a.set_title(t); a.set_xlabel("Longitude (°E)"); a.set_ylabel("Latitude (°N)")
for a,l in zip(axs.ravel(),"ABCD"): lab(a,l)
plt.tight_layout(); save(fig,5)
# ---------- Fig 6: emission + concentration at 29 Apr 12 UTC ----------
v,k=pickle.load(open("kesh/2025042912.pkl","rb")); F,inf=E.emissiya_maydoni(k.U10,k.z0,k.w,k.m_cl,k.lam,k.A_ef,None,CH)
A5=pickle.load(open("frak_5.pkl","rb")); c5=A5["snap"]["choqqi"].sum(0)
from dustflow.grid import Tor
t=Tor(Lx=380e3,Ly=390e3,Hz=5000.0,N=60,M=60,L=30,beta_s=8.0); lon=61.5+t.x/(111320*np.cos(np.deg2rad(40.25))); lat=38.5+t.y/110574
ST={"Bukhara":(39.7762,64.4197),"Navoi":(40.0824,65.3751),"Karshi":(38.8239,65.7658)}
fig,axs=plt.subplots(1,2,figsize=(W,3.0))
for a,(fld,tt,cm,vm) in zip(axs,[(inf["F_tot"]*1e6,r"Dust emission flux ($10^{-6}$ kg m$^{-2}$ s$^{-1}$)","YlOrRd",None),(c5,r"Near-surface concentration (µg/m$^3$)","YlOrRd",np.percentile(c5,99))]):
    im=a.pcolormesh(lon,lat,fld.T,cmap=cm,vmax=vm,shading="auto"); fig.colorbar(im,ax=a,fraction=0.046,pad=0.02)
    q=5; ang=np.deg2rad(k.yonalish); a.quiver(lon[::q],lat[::q],(k.U10*np.cos(ang))[::q,::q].T,(k.U10*np.sin(ang))[::q,::q].T,color="#1a237e",alpha=0.5,scale=220,width=0.003)
    for n,(la,lo) in ST.items(): a.plot(lo,la,"*",ms=7,color="k",mec="w",mew=0.5); a.text(lo+(0.07 if n!="Karshi" else -0.07),la+0.06,n,fontsize=6.5,ha="left" if n!="Karshi" else "right")
    a.set_title(tt); a.set_xlabel("Longitude (°E)"); a.set_ylabel("Latitude (°N)"); a.set_aspect(1/np.cos(np.deg2rad(40.25)))
lab(axs[0],"A"); lab(axs[1],"B"); plt.tight_layout(); save(fig,6)
# ---------- Fig 7: mass budget ----------
T=pd.DataFrame(A5["tar"]); T["t"]=pd.to_datetime(T.t)+pd.Timedelta(hours=1)
fig,axs=plt.subplots(1,2,figsize=(W,2.4)); a=axs[0]
for kk,nm,c in [("Q_em","Emitted","#b03a2e"),("Q_chiq","Exported through boundaries","#e67e22"),("Q_cho","Dry-deposited","#2e7d32"),("Q","Airborne in domain","#1f4e79")]:
    a.plot(T.t,T[kk]/1e6,color=c,lw=1.3,label=nm)
a.set_ylabel("Mass (kt)"); a.legend(frameon=False); a.xaxis.set_major_locator(md.HourLocator(interval=12)); a.xaxis.set_major_formatter(md.DateFormatter("%d Apr\n%H:%M")); lab(a,"A")
a=axs[1]; res=np.abs(T.Q-(T.Q_em-T.Q_cho-T.Q_chiq-T.Q_yut+T.kes))/np.maximum(T.Q_em,1)*100
a.semilogy(T.t,np.maximum(res,1e-6),"o-",ms=2.2,lw=0.9,color="#37474f"); a.set_ylabel("Relative mass-budget residual (%)")
a.xaxis.set_major_locator(md.HourLocator(interval=12)); a.xaxis.set_major_formatter(md.DateFormatter("%d Apr\n%H:%M")); lab(a,"B")
plt.tight_layout(w_pad=1.5); save(fig,7)
# ---------- Fig 8: fraction-resolved vs single mode ----------
A1m=pickle.load(open("frak_1.pkl","rb")); m5=A5["snap"]["ort"]/A5["snap"]["n"]; m1=A1m["snap"]["ort"]/A1m["snap"]["n"]
fig,axs=plt.subplots(2,2,figsize=(W,5.4)); vm=np.percentile(m5,99)
for a,f,tt in [(axs[0,0],m5,"Five transport fractions"),(axs[0,1],m1,"Single effective mode (4.5 µm)")]:
    im=a.pcolormesh(lon,lat,f.T,cmap="YlOrRd",vmax=vm,shading="auto"); fig.colorbar(im,ax=a,fraction=0.046,pad=0.02,label=r"48-h mean (µg/m$^3$)")
    a.set_title(tt); a.set_aspect(1/np.cos(np.deg2rad(40.25))); a.set_xlabel("Longitude (°E)"); a.set_ylabel("Latitude (°N)")
a=axs[1,0]; rel=np.where(m5>np.percentile(m5,10),(m1-m5)/m5*100,np.nan)
im=a.pcolormesh(lon,lat,rel.T,cmap="RdBu_r",vmin=-60,vmax=60,shading="auto"); fig.colorbar(im,ax=a,fraction=0.046,pad=0.02,label="Single mode − five fractions (%)")
a.set_title("Relative difference"); a.set_aspect(1/np.cos(np.deg2rad(40.25))); a.set_xlabel("Longitude (°E)"); a.set_ylabel("Latitude (°N)")
a=axs[1,1]; b5,b1=A5["balans"],A1m["balans"]; lb=["Dry-deposited","Exported","Airborne"]; v5=[b5["Q_cho"],b5["Q_chiq"],b5["Q"]]; v1=[b1["Q_cho"],b1["Q_chiq"],b1["Q"]]
xx=np.arange(3); a.bar(xx-0.2,np.array(v5)/1e6,0.38,color="#b03a2e",label="Five fractions"); a.bar(xx+0.2,np.array(v1)/1e6,0.38,color="#1f4e79",label="Single mode")
for i_ in range(3): a.text(xx[i_]-0.2,v5[i_]/1e6+12,f"{v5[i_]/1e6:.0f}",ha="center",fontsize=7); a.text(xx[i_]+0.2,v1[i_]/1e6+12,f"{v1[i_]/1e6:.0f}",ha="center",fontsize=7)
a.set_xticks(xx); a.set_xticklabels(lb); a.set_ylabel("Mass after 48 h (kt)"); a.legend(frameon=False); a.set_title("Fate of the same 1000.8 kt emitted")
for a,l in zip(axs.ravel(),"ABCD"): lab(a,l)
plt.tight_layout(); save(fig,8)
# ---------- Fig 9: sensitivity ----------
S_=[("Wind speed $U_{10}$",-76.4,150.0,6.00),("Clay fraction $m_{cl}$",-66.8,109.9,4.40),("Soil moisture $w$",29.0,-29.0,1.16),
    ("Erodible fraction $A_{ef}$",-25.0,25.0,1.00),("Roughness length $z_0$",-22.0,20.7,0.88),("Roughness density $\\lambda$",11.6,-11.7,0.47),("Terrain elevation $h$",0.1,0.3,0.01)]
fig,a=plt.subplots(figsize=(W,2.6)); y=np.arange(len(S_))[::-1]
for yy,(n,lo,hi,s) in zip(y,S_):
    a.barh(yy+0.18,lo,0.34,color="#1f4e79"); a.barh(yy-0.18,hi,0.34,color="#b03a2e"); a.text(155,yy,f"$S_p$ = {s:.2f}",va="center",fontsize=7.5)
a.set_yticks(y); a.set_yticklabels([s[0] for s in S_]); a.axvline(0,color="k",lw=0.7); a.set_xlim(-90,190)
a.set_xlabel("Change in domain-mean near-surface concentration (%)")
from matplotlib.patches import Patch
a.legend(handles=[Patch(color="#1f4e79",label="Parameter −25%"),Patch(color="#b03a2e",label="Parameter +25%")],frameon=False,loc="upper center",bbox_to_anchor=(0.5,-0.2),ncol=2)
plt.tight_layout(); save(fig,9)
# ---------- Fig 10: comparison with observations ----------
from netCDF4 import Dataset, num2date
R=json.load(open("uch_tomon.json")); d=pd.read_csv("/home/claude/obs/portal_soatlik.csv"); d["t"]=pd.to_datetime(d.vaqt_utc)
b=d[d.shahar=="bukhara"].set_index("t"); fo=R["stansiya"]["bukhara"]["fon_obs"]; fc=R["stansiya"]["bukhara"]["fon_cams"]
ds=Dataset("/mnt/user-data/uploads/cams_eac4_2025-03-01_2025-05-31.nc"); clon=np.array(ds["longitude"][:]); clat=np.array(ds["latitude"][:])
TT=pd.DatetimeIndex([dt.datetime(x.year,x.month,x.day,x.hour) for x in num2date(ds["valid_time"][:],ds["valid_time"].units)])
ic=int(np.argmin(abs(clon-64.4197))); jc=int(np.argmin(abs(clat-39.7762))); cams=pd.Series(np.array(ds["pm10"][:,jc,ic])*1e9,index=TT)-fc
q=pd.DataFrame(json.load(open("natija_A2.json"))["qator"]); q["t"]=pd.to_datetime(q.vaqt); q=q.set_index("t")
A_,B_="2025-04-28 00:00","2025-04-30 23:00"; ob=(b.pm10-fo).loc[A_:B_]
fig,axs=plt.subplots(1,2,figsize=(W,2.5),gridspec_kw=dict(width_ratios=[2.2,1]))
a=axs[0]; a.fill_between(ob.index,0,ob.clip(lower=0),color="#c7cdd3",label="Observed PM$_{10}$ − background")
a.plot(q.loc[A_:B_].index,q.loc[A_:B_].bukhara_pm10,color="#b03a2e",lw=1.3,label="Model PM$_{10}$ (five fractions)")
cc=cams.loc[A_:B_]; a.plot(cc.index,cc.clip(lower=0),"o-",ms=2.5,lw=1.0,color="#1f4e79",label="CAMS PM$_{10}$ − background")
a.set_ylabel(r"PM$_{10}$ (µg/m$^3$)"); a.set_ylim(0,920); a.legend(frameon=False,loc="upper left",fontsize=7,ncol=1); a.xaxis.set_major_locator(md.HourLocator(interval=12)); a.xaxis.set_major_formatter(md.DateFormatter("%d Apr\n%H:%M")); lab(a,"A")
a=axs[1]; r=R["nisbat"]
a.axhspan(r["obs_min"],r["obs_max"],color="#dfe3e6",label="Observed hourly range"); a.axhline(r["obs_med"],color="#37474f",lw=1.2,label="Observed median")
for x_,v_,c_,n_ in [(0,r["A2"],"#b03a2e","Model"),(1,r["CAMS"],"#1f4e79","CAMS")]:
    a.plot(x_,v_,"D",ms=7,color=c_,mec="k",mew=0.5); a.text(x_+0.14,v_,f"{v_:.2f}",ha="left",va="center",fontsize=7.5)
a.set_xticks([0,1]); a.set_xticklabels(["Model","CAMS"]); a.set_xlim(-0.6,1.7); a.set_ylim(0,0.78); a.set_ylabel(r"PM$_{2.5}$/PM$_{10}$ ratio"); a.legend(frameon=False,loc="upper left",fontsize=7); lab(a,"B")
plt.tight_layout(w_pad=1.2); save(fig,10)
print("Figures 1–10 done")
