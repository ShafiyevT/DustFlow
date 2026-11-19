import sys, json, numpy as np, pandas as pd, rasterio, datetime as dt
sys.path.insert(0,'.')
from netCDF4 import Dataset, num2date
from scipy.interpolate import RegularGridInterpolator
from dustflow.emission import emissiya_maydoni
LAT, LON = 39.7682149, 64.4251505            # qurilish maydoni markazi
MAYDON = 226915.0                             # m², 22,7 ga
A_EF, Z0, LAM = 0.80, 1e-3, 0.0               # qabul qilingan: yalangʻoch, buzilgan grunt
CH=[0.2e-6,2.5e-6,10e-6,20e-6,50e-6,100e-6]
def piksel(f):
    with rasterio.open(f) as s:
        r,c=s.index(LON,LAT); return float(s.read(1)[r,c])
gil=piksel("haqiqiy_malumot/statik/tuproq.tif"); bd=piksel("haqiqiy_malumot/statik/bdod.tif")
sinf=int(piksel("haqiqiy_malumot/statik/sinf.tif")); rel=piksel("haqiqiy_malumot/statik/relyef.tif")
ds=Dataset("haqiqiy_malumot/era5/era5land_2025-04-20_2025-05-01.nc"); v=ds.variables
lat=np.array(v["latitude"][:]); lon=np.array(v["longitude"][:]); o=np.argsort(lat)
T=[dt.datetime(x.year,x.month,x.day,x.hour) for x in num2date(v["valid_time"][:],v["valid_time"].units)]
def nuqta(nom):
    a=np.array(v[nom][:])[:,o,:]
    return np.array([RegularGridInterpolator((lat[o],lon),a[k])([LAT,LON])[0] for k in range(len(T))])
u,vv,t2,sw=nuqta("u10"),nuqta("v10"),nuqta("t2m"),nuqta("swvl1")
q=pd.DataFrame(dict(u10=u,v10=vv,t2m=t2-273.15,swvl1=sw),index=pd.DatetimeIndex(T)).sort_index().loc["2025-04-20":"2025-04-30 23:00"]
q["U10"]=np.hypot(q.u10,q.v10); q["w"]=q.swvl1*1000/(bd*1000)*100
q["qayerdan"]=(np.degrees(np.arctan2(-q.u10,-q.v10))%360)
def em(U):
    a=lambda x: np.array([[x]])
    F,inf=emissiya_maydoni(a(U),a(Z0),a(w_),a(gil),a(LAM),a(A_EF),None,CH)
    return float(inf["F_tot"][0,0]), float(inf["u_star"][0,0]), float(inf["u_star_t"][0,0])
res=[]
for t,r in q.iterrows():
    w_=r.w; F,us,ut=em(r.U10); F7,_,_=em(0.7*r.U10)
    res.append(dict(t=t,F=F,us=us,ut=ut,E=F*MAYDON*3600/1000,E07=F7*MAYDON*3600/1000))
e=pd.DataFrame(res).set_index("t"); q=q.join(e)
print(f"Maydon: {LAT:.4f} N, {LON:.4f} E; yer qoplami sinfi {sinf}; relyef {rel:.0f} m; gil (SoilGrids) {gil:.3f}; zichlik {bd:.2f} g/sm³")
print(f"ERA5-Land: U10 {q.U10.min():.1f}–{q.U10.max():.1f} m/s (maks {q.U10.idxmax():%d.%m %H:%M} UTC), namlik w {q.w.min():.1f}–{q.w.max():.1f} %")
er=q[q.E>0]
print(f"eroziya soatlari (SoilGrids gili bilan): {len(er)} / {len(q)}")
print(f"emissiya maks {q.E.max():.2f} t/soat ({q.E.idxmax():%d.%m %H:%M}); jami 20.04–30.04: {q.E.sum():.1f} t; "
      f"boʻron (28.04 16 – 29.04 23): {q.loc['2025-04-28 16:00':'2025-04-29 23:00'].E.sum():.1f} t")
print(f"shahar ichidagi shamol pasayishi (×0,7) bilan: jami {q.E07.sum():.1f} t, boʻron {q.loc['2025-04-28 16:00':'2025-04-29 23:00'].E07.sum():.1f} t")
b=q.loc["2025-04-29 00:00":"2025-04-29 23:00"]
print(f"29.04 shamol yoʻnalishi (qayerdan): mediana {b.qayerdan.median():.0f}°, U10 oʻrtacha {b.U10.mean():.1f} m/s")
q.to_csv("qurilish_soatlik.csv"); json.dump(dict(gil=gil,bdod=bd,sinf=sinf,relyef=rel,A_ef=A_EF,z0=Z0,maydon=MAYDON),open("qurilish_param.json","w"))
