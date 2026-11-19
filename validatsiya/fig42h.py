import json, pickle, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as md
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"savefig.dpi":300,"figure.dpi":120})
O="/mnt/user-data/outputs/"; s=pickle.load(open("snap42h.pkl","rb")); R=json.load(open("res42h.json"))
lon=61.5+s["x"]/(111320*np.cos(np.deg2rad(40.25))); lat=38.5+s["y"]/110574
ST={"Buxoro":(39.7762,64.4197),"Navoiy":(40.0824,65.3751),"Qarshi":(38.8239,65.7658)}
def bezak(a):
    for n,(la,lo) in ST.items():
        a.plot(lo,la,"*",ms=10,color="k",mec="white",mew=0.7); a.text(lo+0.08,la+0.06,n,fontsize=7.5,color="k")
    a.set_xlabel("uzunlik, °E"); a.set_ylabel("kenglik, °N"); a.set_aspect(1/np.cos(np.deg2rad(40.25)))
# 4.10 emissiya
fig,ax=plt.subplots(1,3,figsize=(15.2,4.8))
for a,(d,t,c) in zip(ax,[(s["us"],"a) dinamik tezlik  $u_*$, m/s","viridis"),
                        (np.minimum(s["ut"],1.5),"b) samarali chegaraviy tezlik  $u_{*t}^{ef}$, m/s","magma"),
                        (s["F"]*1e6,"c) emissiya oqimi  $F$,  $10^{-6}$ kg/(m²·s)","YlOrRd")]):
    im=a.pcolormesh(lon,lat,d.T,cmap=c,shading="auto"); fig.colorbar(im,ax=a,fraction=0.046,pad=0.03); a.set_title(t); bezak(a)
fig.suptitle("Emissiya sxemasining natijalari: 29.04.2025, 12:00 UTC (ERA5-Land)",fontsize=13,fontweight="bold",y=1.02)
plt.tight_layout(); plt.savefig(O+"rasm_4_10_emissiya.png",bbox_inches="tight",facecolor="white",pad_inches=0.2); plt.close()
# 4.11 konsentratsiya
fig,a=plt.subplots(figsize=(9,7.2)); y=s["yuza"]
im=a.pcolormesh(lon,lat,y.T,cmap="YlOrRd",shading="auto",vmin=0,vmax=np.percentile(y,99))
fig.colorbar(im,ax=a,fraction=0.046,pad=0.03).set_label("yer sirtidagi konsentratsiya, mkg/m³")
a.contour(lon,lat,s["eta"].T,levels=[300,600,1000,1500],colors="#5d4037",linewidths=0.7,alpha=0.6)
k=5; a.quiver(lon[::k],lat[::k],s["U"][::k,::k].T,s["V"][::k,::k].T,color="#1a237e",alpha=0.55,scale=200,width=0.0032)
bezak(a); a.set_title("Yer sirtiga yaqin qatlamdagi chang konsentratsiyasi, 29.04.2025 12:00 UTC")
fig.text(0.5,-0.01,"izoliniyalar — relyef (300, 600, 1000, 1500 m), strelkalar — shamol, ★ — Oʻzgidromet stansiyalari",ha="center",fontsize=8.6,style="italic",color="#555")
plt.tight_layout(); plt.savefig(O+"rasm_4_11_konsentratsiya.png",bbox_inches="tight",facecolor="white",pad_inches=0.22); plt.close()
# 4.12 profil va fraksiyalar
fig,ax=plt.subplots(1,2,figsize=(12.6,5.1))
for (c,z),nm,col in [(s["prof_chol"],"Qizilqum (63,5°E; 40,8°N)","#c0392b"),(s["prof_voha"],"Buxoro stansiyasi katagi","#2c7a4b")]:
    ax[0].plot(c,z/1000,lw=2.3,color=col,label=nm)
ax[0].set_xscale("log"); ax[0].set_xlabel("konsentratsiya, mkg/m³"); ax[0].set_ylabel("yer sirtidan balandlik, km")
ax[0].set_ylim(0,3); ax[0].set_title("a) vertikal profillar, 29.04 12:00 UTC"); ax[0].grid(alpha=0.3,which="both"); ax[0].legend(fontsize=9)
nm=["PM2.5","PM10\n(2,5–10)","10–20 µm","20–50 µm","50–100 µm"]; v=np.array(s["frak"])/1e6
ax[1].bar(nm,v,color=["#1f6fb2","#2c7a4b","#d77a3a","#c0392b","#8e44ad"],edgecolor="k",lw=0.6)
for i,x in enumerate(v): ax[1].text(i,x*1.02,f"{x:.1f}",ha="center",fontsize=9)
ax[1].set_ylabel("sohadagi massa, ming tonna"); ax[1].set_title("b) fraksiyalar boʻyicha taqsimot"); ax[1].grid(alpha=0.3,axis="y")
plt.tight_layout(); plt.savefig(O+"rasm_4_12_profil.png",bbox_inches="tight",facecolor="white",pad_inches=0.2); plt.close()
# 4.13 balans
T=pd.DataFrame(R["tarix"]); T["t"]=pd.to_datetime(T.t)
fig,ax=plt.subplots(1,2,figsize=(12.6,4.7)); a=ax[0]
for kk,nm_,c,ls in [("Q_em","sirtdan chiqqan","#c0392b","-"),("Q_chiq","chegaradan chiqqan","#d77a3a","-"),("Q_cho","sirtga choʻkkan","#2c7a4b","-"),("Q","sohada muallaq","#1f6fb2","-"),("Q_yut","atmosferada yutilgan","#8e44ad","--")]:
    a.plot(T.t,T[kk]/1e6,lw=2.1,color=c,ls=ls,label=nm_)
a.set_ylabel("massa, ming tonna"); a.set_title("a) massa balansining tashkil etuvchilari"); a.grid(alpha=0.3); a.legend(fontsize=8.5)
a.xaxis.set_major_locator(md.HourLocator(interval=12)); a.xaxis.set_major_formatter(md.DateFormatter("%d.%m\n%H:%M")); a.set_xlabel("vaqt (UTC)")
a=ax[1]; nom=np.abs(T.qol)/np.maximum(T.Q_em,1e-9)*100
a.semilogy(T.t,np.maximum(nom,1e-8),"o-",ms=3,lw=1.6,color="#37474f"); a.axhline(0.01,ls="--",color="r",lw=1)
a.text(T.t.iloc[30],0.0088,"talab: 0,01 %",color="r",fontsize=8.5)
a.set_ylabel("nisbiy nomuvofiqlik, %"); a.set_title("b) balansning bajarilish aniqligi"); a.grid(alpha=0.3,which="both")
a.xaxis.set_major_locator(md.HourLocator(interval=12)); a.xaxis.set_major_formatter(md.DateFormatter("%d.%m\n%H:%M")); a.set_xlabel("vaqt (UTC)")
plt.tight_layout(); plt.savefig(O+"rasm_4_13_balans.png",bbox_inches="tight",facecolor="white",pad_inches=0.2); plt.close()
print("4.10–4.13 tayyor")
