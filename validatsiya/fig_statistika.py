import csv, json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"savefig.dpi":300,"figure.dpi":120})
rows=list(csv.DictReader(open('/mnt/user-data/uploads/sdmx_data_1569__1_.csv',encoding='utf-8-sig')))
yil=list(range(2010,2026)); r=[x for x in rows if x['Klassifikator_ru']=='Бухарская область'][0]
bux=np.array([float(r[str(y)]) for y in yil])
V=json.load(open("viloyat_emissiya.json")); MODEL=V["viloyat_boron"]/1e3; PAST=MODEL/3; QATTIQ=0.15
fig,axs=plt.subplots(1,2,figsize=(13.0,4.9))
a=axs[0]
a.bar(yil,bux,color="#1f6fb2",edgecolor="k",lw=0.5,label="barcha moddalar")
a.bar(yil,bux*QATTIQ,color="#c0392b",edgecolor="k",lw=0.5,label="shundan qattiq zarrachalar (baho)")
a.set_xlabel("yil"); a.set_ylabel("emissiya, ming tonna/yil"); a.set_title("a) Buxoro viloyatida qayd etilgan emissiya")
a.grid(alpha=0.3,axis="y"); a.legend(fontsize=8.6); a.set_xticks(yil[::2]); a.tick_params(axis='x',labelsize=8.5)
for y,v in zip(yil,bux):
    if y in (2010,2019,2025): a.text(y,v+1.5,f"{v:.1f}",ha="center",fontsize=8.2)
a=axs[1]
NOM=["Sanoat,\nbir yil\n(2025)","Sanoat,\nqattiq zarracha\n(2025, baho)","Shamol eroziyasi,\n28–29 aprel 2025\nboʻroni (model)"]
VAL=[bux[-1],bux[-1]*QATTIQ,MODEL]
a.bar(NOM,VAL,color=["#1f6fb2","#c0392b","#d77a3a"],edgecolor="k",lw=0.6)
a.errorbar([2],[MODEL],yerr=[[MODEL-PAST],[0]],fmt="none",ecolor="k",capsize=6,lw=1.5)
a.text(2.28,PAST,f"÷3: {PAST:.0f}",fontsize=8.3,va="center")
a.set_yscale("log"); a.set_ylabel("massa, ming tonna"); a.set_title("b) kattalik tartibi boʻyicha taqqoslash (viloyat chegarasida)")
a.grid(alpha=0.3,axis="y",which="both"); a.set_ylim(1,3000)
for i,v in enumerate(VAL): a.text(i,v*1.18,f"{v:.1f}",ha="center",fontsize=10,fontweight="bold")
a.annotate("",xy=(2,MODEL*0.85),xytext=(1,bux[-1]*QATTIQ*1.2),arrowprops=dict(arrowstyle="<->",lw=1.6,color="#37474f"))
a.text(1.5,45,f"{PAST/(bux[-1]*QATTIQ):.0f}–{MODEL/(bux[-1]*QATTIQ):.0f} barobar",fontsize=9.5,ha="center",color="#37474f",fontweight="bold",bbox=dict(fc="white",ec="none",alpha=0.85,pad=1.5))
fig.text(0.5,-0.02,"Manba: Oʻzbekiston Respublikasi Statistika agentligi, 1569-koʻrsatkich (siat.stat.uz); model — ERA5-Land majburlashi, Buxoro viloyati chegarasi ichida;\n"
         "xato chizigʻi — stansiya taqqoslashidagi ortiqcha baholashni hisobga olgan pastki baho",ha="center",fontsize=8.2,style="italic",color="#555")
plt.tight_layout(); plt.savefig('/mnt/user-data/outputs/rasm_4_21_statistika.png',bbox_inches="tight",facecolor="white",pad_inches=0.25)
print(f"viloyat boʻroni {MODEL:.1f}, pastki {PAST:.1f}, nisbat {PAST/(bux[-1]*QATTIQ):.0f}–{MODEL/(bux[-1]*QATTIQ):.0f}")
