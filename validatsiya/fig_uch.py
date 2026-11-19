import json, numpy as np, pandas as pd, datetime as dt, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as md
from netCDF4 import Dataset, num2date
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9.5,"savefig.dpi":300,"figure.dpi":120})
R=json.load(open("uch_tomon.json")); ST={"bukhara":("Buxoro",39.7762,64.4197),"navoi":("Navoiy",40.0824,65.3751),"qarshi":("Qarshi",38.8239,65.7658)}
d=pd.read_csv("/home/claude/obs/portal_soatlik.csv"); d["t"]=pd.to_datetime(d.vaqt_utc)
ds=Dataset('/mnt/user-data/uploads/cams_eac4_2025-03-01_2025-05-31.nc'); clon=np.array(ds['longitude'][:]); clat=np.array(ds['latitude'][:])
T=pd.DatetimeIndex([dt.datetime(x.year,x.month,x.day,x.hour) for x in num2date(ds['valid_time'][:],ds['valid_time'].units)]); P10=np.array(ds['pm10'][:])*1e9
Q={V:pd.DataFrame(json.load(open(f"natija_{V}.json"))["qator"]).assign(t=lambda x:pd.to_datetime(x.vaqt)).set_index("t") for V in ["A1","A2"]}
A,B="2025-04-28 00:00","2025-04-30 23:00"
fig=plt.figure(figsize=(15,9.6)); gs=fig.add_gridspec(3,2,width_ratios=[2.6,1])
for n,(s,(nm,la,lo)) in enumerate(ST.items()):
    a=fig.add_subplot(gs[n,0]); r=R["stansiya"][s]; k=R["kun"][s]
    ob=(d[d.shahar==s].set_index("t").pm10-r["fon_obs"]).loc[A:B]
    i=int(np.argmin(abs(clon-lo))); j=int(np.argmin(abs(clat-la))); ce=(pd.Series(P10[:,j,i],index=T)-r["fon_cams"]).loc[A:B]
    a.fill_between(ob.index,0,ob.clip(lower=0),color="#bdc3c7",label="kuzatuv − fon")
    a.plot(Q["A1"].loc[A:B].index,Q["A1"].loc[A:B][f"{s}_pm10"],lw=1.9,color="#d35400",label="DustFlow (CAMS chegarasi bilan)")
    a.plot(Q["A2"].loc[A:B].index,Q["A2"].loc[A:B][f"{s}_pm10"],lw=1.6,ls="--",color="#f0b27a",label="DustFlow (faqat mahalliy)")
    a.plot(ce.index,ce.clip(lower=0),"o-",ms=4,lw=1.5,color="#1f6fb2",label="CAMS − fon")
    a.set_title(f"{'abc'[n]}) {nm}:  r = {r['A1']['r']:.2f} (DustFlow),  {r['CAMS']['r']:.2f} (CAMS);   "
                f"boʻron kuni: kuzatuv {k['obs']:.0f}, DustFlow {k['A1']:.0f} / {k['A2']:.0f}, CAMS {k['CAMS']:.0f} mkg/m³",fontsize=9.2)
    a.set_ylabel("PM10, mkg/m³"); a.grid(alpha=0.3); a.xaxis.set_major_locator(md.HourLocator(interval=12)); a.xaxis.set_major_formatter(md.DateFormatter("%d.%m %H:%M"))
    if n==0: a.legend(fontsize=7.8,loc="upper right",ncol=2)
a=fig.add_subplot(gs[0:2,1]); p=R["pool"]
x=np.arange(3); w=0.26
for i_,(kk,c,nm) in enumerate([("A1","#d35400","DustFlow\n(chegara bilan)"),("A2","#f0b27a","DustFlow\n(mahalliy)"),("CAMS","#1f6fb2","CAMS")]):
    v=[p[kk]["r"],p[kk]["FAC2"],abs(p[kk]["FB"])]
    a.bar(x+(i_-1)*w,v,w,color=c,edgecolor="k",lw=0.5,label=nm.replace("\n"," "))
    for xx,vv in zip(x+(i_-1)*w,v): a.text(xx,vv+0.01,f"{vv:.2f}",ha="center",fontsize=7.6)
a.plot([0.6,1.4],[0.5,0.5],"r--",lw=1.4); a.text(1.42,0.5,"FAC2 > 0,5",color="r",fontsize=8,va="center")
a.plot([1.6,2.4],[0.3,0.3],"r--",lw=1.4); a.text(2.42,0.3,"|FB| < 0,3",color="r",fontsize=8,va="center")
a.set_xticks(x); a.set_xticklabels(["r","FAC2","|FB|"]); a.set_ylim(0,0.72); a.set_xlim(-0.5,2.95)
a.set_title("d) 3 stansiya, 71 juftlik, 3 soatlik"); a.legend(fontsize=7.8,loc="upper left"); a.grid(alpha=0.3,axis="y")
a=fig.add_subplot(gs[2,1]); q=R["nisbat"]
a.axhspan(q["obs_min"],q["obs_max"],color="#d5dbdb",label=f"kuzatuv: soatlik oraliq ({q['obs_min']:.2f}–{q['obs_max']:.2f})")
a.axhline(q["obs_med"],color="#2c3e50",lw=1.5,label=f"kuzatuv: mediana ({q['obs_med']:.2f})")
for xx,v,c,nm in [(0,q["A1"],"#d35400","DustFlow\n(chegara)"),(1,q["A2"],"#f0b27a","DustFlow\n(mahalliy)"),(2,q["CAMS"],"#1f6fb2","CAMS")]:
    a.plot(xx,v,"D",ms=10,color=c,mec="k",zorder=5); a.text(xx,v+0.035,f"{v:.2f}",ha="center",fontsize=8.5,fontweight="bold")
a.set_xticks([0,1,2]); a.set_xticklabels(["DustFlow\n(chegara)","DustFlow\n(mahalliy)","CAMS"],fontsize=8)
a.set_xlim(-0.5,2.5); a.set_ylim(0,0.6); a.set_ylabel("PM2.5 / PM10"); a.set_title("e) boʻrondagi zarracha oʻlchami, Buxoro"); a.legend(fontsize=7.2,loc="upper left"); a.grid(alpha=0.3,axis="y")
fig.text(0.5,0.002,"28–30 aprel 2025. Fon — har bir manba uchun 20–26 aprel medianasi (kuzatuv va CAMS alohida). d) panelda qizil chiziqlar — Chang–Hanna chegaralari.",
         ha="center",fontsize=8.2,style="italic",color="#555")
plt.tight_layout(rect=[0,0.015,1,1]); plt.savefig('/mnt/user-data/outputs/rasm_4_uch_tomonlama.png',bbox_inches="tight",facecolor="white",pad_inches=0.2); print("ok")
