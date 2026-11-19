import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as md
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9.5,"savefig.dpi":300,"figure.dpi":120})
d=pd.read_csv("/home/claude/obs/portal_soatlik.csv"); d["t"]=pd.to_datetime(d["vaqt_utc"])
ST=[("bukhara","Buxoro"),("navoi","Navoiy"),("qarshi","Qarshi")]
fon={s:d[(d.shahar==s)&(d.t>="2025-04-20")&(d.t<="2025-04-26 23:00")].pm10.median() for s,_ in ST}
Q={V:pd.DataFrame(json.load(open(f"natija_{V}.json"))["qator"]).assign(t=lambda x:pd.to_datetime(x.vaqt)).set_index("t") for V in ["A1","A2"]}
B=json.load(open("baho_A.json"))
fig=plt.figure(figsize=(14.5,9.2)); gs=fig.add_gridspec(3,3,width_ratios=[2.2,2.2,1.3])
for n,(s,nm) in enumerate(ST):
    a=fig.add_subplot(gs[n,:2]); ob=d[d.shahar==s].set_index("t").pm10.loc["2025-04-27":"2025-04-30 23:00"]-fon[s]
    a.fill_between(ob.index,0,ob.clip(lower=0),color="#bdc3c7",label="kuzatuv − fon")
    a.plot(Q["A1"].index,Q["A1"][f"{s}_pm10"],lw=1.8,color="#1f6fb2",label="A1: CAMS chegarasi bilan")
    a.plot(Q["A2"].index,Q["A2"][f"{s}_pm10"],lw=1.6,color="#e67e22",ls="--",label="A2: faqat mahalliy")
    a.axvspan(pd.Timestamp("2025-04-27"),pd.Timestamp("2025-04-28"),color="#f2f3f4",zorder=0)
    p1,p2=B["A1"]["stansiya"][s],B["A2"]["stansiya"][s]
    a.set_title(f"{'abc'[n]}) {nm}:  A1 r={p1['r']:+.2f}, NMB={p1['NMB']:+.0f}%   |   A2 r={p2['r']:+.2f}, NMB={p2['NMB']:+.0f}%",fontsize=9.8)
    a.set_ylabel("PM10, mkg/m³"); a.grid(alpha=0.3); a.xaxis.set_major_formatter(md.DateFormatter("%d.%m %H:%M"))
    if n==0: a.legend(fontsize=8,loc="upper left"); a.text(pd.Timestamp("2025-04-27 02:00"),a.get_ylim()[1]*0.85,"moslashish\ndavri",fontsize=7.5,color="#7f8c8d")
a=fig.add_subplot(gs[:2,2])
for V,c,mk in [("A1","#1f6fb2","o"),("A2","#e67e22","s")]:
    j=np.array(B[V]["kunlik_juft"]); a.scatter(np.maximum(j[:,0],1),np.maximum(j[:,1],1),c=c,marker=mk,s=45,edgecolor="k",lw=0.4,label=f"{V} (FAC2={B[V]['kunlik']['FAC2']:.2f})")
q=np.array([1,2000]); a.plot(q,q,"k-",lw=1); a.fill_between(q,q/2,q*2,color="#abebc6",alpha=0.35)
a.set_xscale("log"); a.set_yscale("log"); a.set_xlim(5,1500); a.set_ylim(1,1500)
a.set_xlabel("kuzatuv − fon, mkg/m³"); a.set_ylabel("model, mkg/m³"); a.set_title("d) kunlik oʻrtachalar (9 juftlik)"); a.legend(fontsize=7.8); a.grid(alpha=0.3,which="both")
a=fig.add_subplot(gs[2,2]); a.axis("off")
qat=[("Choʻqqi ±3 soat","✓"),("Soatlik C–H oʻtmaydi","✓"),("Soatlik FAC2 0,25–0,5","✗ 0,23"),("Soatlik r 0,2–0,6","✓ 0,28"),
     ("Kunlik FAC2 ≥ 0,5","✗ 0,33"),("PM2.5/PM10 0,10–0,20","✗ 0,23"),("NMB(A2) < NMB(A1)","✓")]
a.text(0,1,"e) qayd №2 bashoratlari (A1)",fontweight="bold",fontsize=9.5,va="top")
for i,(t_,v) in enumerate(qat):
    a.text(0,0.86-i*0.12,t_,fontsize=8.6,va="top"); a.text(0.78,0.86-i*0.12,v,fontsize=8.6,va="top",color="#1e8449" if v.startswith("✓") else "#c0392b",fontweight="bold")
plt.tight_layout(); plt.savefig('/mnt/user-data/outputs/rasm_4_26_stansiyalar.png',bbox_inches="tight",facecolor="white",pad_inches=0.2); print("ok")
