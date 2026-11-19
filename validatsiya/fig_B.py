import sys, glob, pickle, json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as md
sys.path.insert(0,'.')
from dustflow.emission import emissiya_maydoni
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9.5,"savefig.dpi":300,"figure.dpi":120})
CH=[0.2e-6,2.5e-6,10e-6,20e-6,50e-6,100e-6]
def qator(papka):
    r=[]
    for f in sorted(glob.glob(f"{papka}/*.pkl")):
        v,k=pickle.load(open(f,"rb")); F,inf=emissiya_maydoni(k.U10,k.z0,k.w,k.m_cl,k.lam,k.A_ef,None,CH)
        m=k.A_ef>0.1; r.append((v,float(np.max(inf["u_star"][m]/inf["u_star_t"][m])),float(np.median(k.w[m]))))
    return pd.DataFrame(r,columns=["t","nisbat","w"]).set_index("t")
fb,fa=qator("keshB"),qator("kesh")
d=pd.read_csv("/home/claude/obs/portal_soatlik.csv"); d["t"]=pd.to_datetime(d.vaqt_utc)
q=pd.DataFrame(json.load(open("natija_B.json"))["qator"]); q["t"]=pd.to_datetime(q.vaqt); q=q.set_index("t")
fig,ax=plt.subplots(1,3,figsize=(15,4.4))
a=ax[0]
for s,c,nm in [("bukhara","#c0392b","Buxoro"),("qarshi","#8e44ad","Qarshi")]:
    fon=d[(d.shahar==s)&(d.t>="2026-02-14")&(d.t<="2026-02-14 23:00")].pm10.median()
    ob=d[d.shahar==s].set_index("t").pm10.loc["2026-02-14":"2026-02-16 23:00"]-fon
    a.plot(ob.index,ob.clip(lower=1),lw=1.5,color=c,label=f"{nm}: kuzatuv − fon")
    a.plot(q.index,np.maximum(q[f"{s}_pm10"],1),lw=1.2,ls="--",color=c,alpha=0.6,label=f"{nm}: model")
a.set_yscale("log"); a.set_ylim(1,1e4); a.set_ylabel("PM10, mkg/m³"); a.set_title("a) 14–16 fevral 2026: kuzatuv va model")
a.legend(fontsize=7.8); a.grid(alpha=0.3,which="both"); a.xaxis.set_major_formatter(md.DateFormatter("%d.%m %H"))
a=ax[1]
a.plot(np.arange(len(fa)),fa.nisbat.values,lw=1.8,color="#e67e22",label="aprel 2025 (27.04–30.04)")
a.plot(np.arange(len(fb)),fb.nisbat.values,lw=1.8,color="#1f6fb2",label="fevral 2026 (14.02–16.02)")
a.axhline(1,color="k",lw=1.3,ls="--"); a.text(2,1.05,"eroziya chegarasi",fontsize=8.3)
a.set_xlabel("hisoblash boshidan soatlar"); a.set_ylabel("choʻlda maks. $u_*/u_{*t}$"); a.set_title("b) eroziya shartining bajarilishi")
a.legend(fontsize=8); a.grid(alpha=0.3)
a=ax[2]
a.bar(["aprel\n29.04 12:00","fevral\n15.02 09:00"],[fa.loc["2025-04-29 12:00","w"],fb.loc["2026-02-15 09:00","w"]],color=["#e67e22","#1f6fb2"],edgecolor="k")
for i,v in enumerate([fa.loc["2025-04-29 12:00","w"],fb.loc["2026-02-15 09:00","w"]]): a.text(i,v+0.5,f"{v:.1f} %",ha="center",fontsize=10,fontweight="bold")
a.set_ylabel("choʻl tuprogʻi namligi (mediana), %"); a.set_title("c) ERA5-Land boʻyicha tuproq namligi"); a.grid(alpha=0.3,axis="y")
plt.tight_layout(); plt.savefig('/mnt/user-data/outputs/rasm_4_27_fevral.png',bbox_inches="tight",facecolor="white",pad_inches=0.2); print("ok")
