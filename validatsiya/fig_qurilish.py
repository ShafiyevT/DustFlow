import json, pickle, numpy as np, pandas as pd, matplotlib, sys
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as md
sys.path.insert(0,'.')
from dustflow.emission import emissiya_maydoni
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9.8,"savefig.dpi":300,"figure.dpi":120})
q=pd.read_csv("qurilish_soatlik.csv",index_col=0,parse_dates=True).loc["2025-04-28 00:00":"2025-04-30 12:00"]
J=json.load(open("qurilish_matritsa.json")); CH=[0.2e-6,2.5e-6,10e-6,20e-6,50e-6,100e-6]
def E(g,w,U): 
    a=lambda x: np.array([[x]]); F,i=emissiya_maydoni(a(U),a(1e-3),a(w),a(g),a(0.0),a(0.8),None,CH); return i["F_tot"][0,0]*226915*3.6
e10=np.array([E(0.10,1.0,u) for u in q.U10]); e20=np.array([E(0.20,1.0,u) for u in q.U10]); e15=np.array([E(0.15,1.0,u) for u in q.U10])
e15e=np.array([E(0.15,w,u) for u,w in zip(q.U10,q.w)])
fig,ax=plt.subplots(1,2,figsize=(14.5,4.8),gridspec_kw=dict(width_ratios=[1.7,1]))
a=ax[0]; a.fill_between(q.index,e10,e20,color="#f5cba7",alpha=0.8,label="quruq grunt, gil 0,10–0,20")
a.plot(q.index,e15,lw=2.2,color="#d35400",label="quruq grunt, gil 0,15 (markaziy holat)")
a.plot(q.index,e15e,lw=1.8,ls="--",color="#1f6fb2",label="ERA5 namligi, gil 0,15")
a.axhline(0,color="#2e7d32",lw=2.5,label="namlangan sirt (15 %) — barcha holatlarda 0")
a.set_ylabel("emissiya, t/soat"); a.set_yscale("symlog",linthresh=0.1); a.set_ylim(0,20); a.grid(alpha=0.3,which="both")
b=a.twinx(); b.plot(q.index,q.U10,color="#555",lw=1,alpha=0.7); b.set_ylabel("ERA5-Land $U_{10}$, m/s",color="#555"); b.set_ylim(0,24)
a.set_title("a) qurilish maydonidan chang emissiyasi, 28–30 aprel 2025"); a.legend(fontsize=7.8,loc="upper left")
a.xaxis.set_major_locator(md.HourLocator(interval=12)); a.xaxis.set_major_formatter(md.DateFormatter("%d.%m\n%H:%M"))
a=ax[1]; g=[0.05,0.10,0.15,0.20]; x=np.arange(4); w=0.38
qv=[J[str(k)]["boron"]["quruq"] for k in g]; ev=[J[str(k)]["boron"]["era5"] for k in g]
for xs,vals,c,nm in [(x-w/2,qv,"#d35400","quruq grunt"),(x+w/2,ev,"#1f6fb2","ERA5 namligi")]:
    vv=np.array(vals); ok=vv>0
    a.bar(xs[ok],vv[ok],w,color=c,edgecolor="k",lw=0.5,label=nm)
    for xx,v in zip(xs,vv): a.text(xx,(v*1.25 if v>0 else 0.06),f"{v:.1f}" if v>0 else "0",ha="center",fontsize=8.5,color="k" if v>0 else c,fontweight="normal" if v>0 else "bold")
a.set_yscale("log"); a.set_ylim(0.04,1500); a.set_xticks(x); a.set_xticklabels([f"{k:.2f}" for k in g]); a.set_xlabel("gil ulushi $m_{cl}$")
a.set_ylabel("boʻron davomidagi emissiya, t"); a.set_title("b) emissiya: gil ulushi va sirt holati"); a.legend(fontsize=8,loc="upper left"); a.grid(alpha=0.3,axis="y",which="both")
a.text(3.45,600,"namlangan sirt:\nbarcha holatlarda 0",ha="right",va="top",fontsize=8.3,color="#2e7d32")
plt.tight_layout(); plt.savefig('/mnt/user-data/outputs/rasm_4_21_qurilish_emissiya.png',bbox_inches="tight",facecolor="white",pad_inches=0.2); plt.close()
R=pickle.load(open("qurilish_natija.pkl","rb")); y=R["yig"]; x=(R["x"]-10000)/1000; yy=(R["y"]-10000)/1000
fig,ax=plt.subplots(1,3,figsize=(15.5,5.0))
for a,(f,t_,cm,lv) in zip(ax,[(y["ort"],"a) 32 soatlik oʻrtacha PM10, mkg/m³","YlOrRd",[25,75]),
                            (y["maks"],"b) soatlik maksimum PM10, mkg/m³","YlOrRd",[25,75,150]),
                            (R["qal"]*1000,"c) choʻkma qalinligi, mkm","YlOrBr",[0.1,1.0])]):
    im=a.pcolormesh(x,yy,f.T,cmap=cm,shading="auto",vmin=0,vmax=np.percentile(f,99.9))
    cs=a.contour(x,yy,f.T,levels=lv,colors="k",linewidths=0.9); a.clabel(cs,fmt=lambda v: f"{v:g}",fontsize=7.5)
    fig.colorbar(im,ax=a,fraction=0.046,pad=0.03)
    a.add_patch(plt.Rectangle((-0.24,-0.24),0.48,0.48,fill=False,ec="#1f6fb2",lw=1.8))
    a.plot(-0.47,0.89,"*",ms=13,color="#1f6fb2",mec="white"); a.text(-0.4,1.05,"Oʻzgidromet\nstansiyasi",fontsize=7.5,color="#1f6fb2")
    a.set_xlim(-3,3); a.set_ylim(-5,1.6); a.set_aspect(1); a.set_xlabel("sharq, km"); a.set_ylabel("shimol, km"); a.set_title(t_,fontsize=10)
ax[0].annotate("",xy=(2.3,-0.4),xytext=(2.55,1.2),arrowprops=dict(arrowstyle="-|>",color="#1a237e",lw=2))
ax[0].text(1.6,1.3,"shamol (NNE)",fontsize=8,color="#1a237e")
fig.text(0.5,-0.02,"Markaziy holat: quruq grunt, gil 0,15; 28.04 16:00 – 29.04 23:00 UTC, ERA5-Land soatlik shamoli. Koʻk kvadrat — qurilish maydoni (22,7 ga).",ha="center",fontsize=8.3,style="italic",color="#555")
plt.tight_layout(); plt.savefig('/mnt/user-data/outputs/rasm_4_22_qurilish_tarqalish.png',bbox_inches="tight",facecolor="white",pad_inches=0.2)
print("ok")
