"""Ola Bengaluru Ride Intelligence - analysis engine.
Raw CSV -> audit vs. the project brief -> docs/metrics.json + docs/index.html"""
import json, pathlib, numpy as np, pandas as pd
from scipy.stats import chi2_contingency
R = pathlib.Path(__file__).resolve().parents[1]
d = pd.read_csv(R/"data/bookings_july_2024.csv", parse_dates=["Date"])
d["ok"] = d.Booking_Status.eq("Success"); d["hr"] = d.Date.dt.hour; d["dow"] = d.Date.dt.dayofweek
n = len(d); pct = lambda s: round(100*float(s.mean()), 2)
s = d[d.ok]; wk = d.dow.ge(5); day_n = d.groupby(d.Date.dt.date).size()
wk_days = day_n[[x.weekday() >= 5 for x in day_n.index]].mean(); wd_days = day_n[[x.weekday() < 5 for x in day_n.index]].mean()
cc, dc = pct(d.Booking_Status.eq("Canceled by Customer")), pct(d.Booking_Status.eq("Canceled by Driver"))
u500, m1k = pct(d.Booking_Value < 500), pct(d.Booking_Value.between(500, 999))
inc = pct(s.Incomplete_Rides.eq("Yes"))
spec = [("Overall success rate", "62%", pct(d.ok), abs(pct(d.ok)-62) < 1),
 ("Cancelled by customer", "<= 7%", cc, cc <= 7),
 ("Cancelled by driver", "<= 18%", dc, dc <= 18),
 ("Incomplete (of successful rides)", "< 6%", inc, inc < 6),
 ("Orders under Rs 500", "70%", u500, abs(u500-70) < 3),
 ("Orders Rs 500-999", "28%", m1k, abs(m1k-28) < 3),
 ("Weekend orders/day vs weekday", "higher", round(wk_days/wd_days, 3), wk_days > wd_days),
 ("Weekend avg fare vs weekday", "higher", round(d[wk].Booking_Value.mean()/d[~wk].Booking_Value.mean(), 3), d[wk].Booking_Value.mean() > d[~wk].Booking_Value.mean())]
st = d.groupby("Booking_Status").agg(n=("ok", "size"), gmv=("Booking_Value", "sum")).reset_index()
veh = d.groupby("Vehicle_Type").apply(lambda g: pd.Series({"n": len(g), "success": pct(g.ok),
      "km": round(g[g.ok].Ride_Distance.mean(), 1), "fare": round(g[g.ok].Booking_Value.mean()),
      "rs_km": round(g[g.ok].Booking_Value.sum()/g[g.ok].Ride_Distance.sum(), 1)}), include_groups=False).reset_index()
z = d.groupby("Pickup_Location").ok.agg(["sum", "size"]).reset_index(); z["rate"] = 100*z["sum"]/z["size"]
z["se"] = 196*np.sqrt((z.rate/100)*(1-z.rate/100)/z["size"])
chi_p = chi2_contingency(np.c_[z["sum"], z["size"]-z["sum"]])[1]
cnt = lambda c: d[c].value_counts().rename_axis("k").reset_index(name="v").values.tolist()
day = d.groupby(d.Date.dt.day).agg(n=("ok", "size"), ok=("ok", "mean")).reset_index()
M = dict(rows=n, gmv=int(d.Booking_Value.sum()), realized=int(s.Booking_Value.sum()), spec=spec,
 status=st.values.tolist(), veh=veh.values.tolist(), zones=z.sort_values("rate")[["Pickup_Location", "rate", "se", "size"]].round(2).values.tolist(),
 zone_p=round(float(chi_p), 3), reasons_c=cnt("Canceled_Rides_by_Customer"), reasons_d=cnt("Canceled_Rides_by_Driver"),
 pay=s.groupby("Payment_Method").Booking_Value.sum().reset_index().values.tolist(), daily=day.round(3).values.tolist(),
 hourly=d.groupby("hr").size().tolist(), sim={k: {"n": int(r.n), "avg": round(r.gmv/r.n)} for k, r in st.set_index("Booking_Status").iterrows()},
 corr_fare_km=round(float(np.corrcoef(s.Ride_Distance, s.Booking_Value)[0, 1]), 3),
 corr_ratings=round(float(np.corrcoef(s.Driver_Ratings, s.Customer_Rating)[0, 1]), 3),
 scatter=s.sample(300, random_state=7)[["Ride_Distance", "Booking_Value"]].values.tolist(),
 same_pd=int(d.Pickup_Location.eq(d.Drop_Location).sum()), absurd=int((s.Booking_Value/s.Ride_Distance).gt(100).sum()),
 uniq_cust=int(d.Customer_ID.nunique()))
M["leak"] = M["gmv"] - M["realized"]
(R/"docs/metrics.json").write_text(json.dumps(M, default=float))
tpl = R/"src/dashboard_template.html"
if tpl.exists(): (R/"docs/index.html").write_text(tpl.read_text().replace("/*DATA*/", "window.DATA=" + json.dumps(M, default=float)))
print({k: M[k] for k in ["rows", "gmv", "realized", "leak", "zone_p", "corr_fare_km", "corr_ratings", "same_pd", "absurd", "uniq_cust"]})
for r in spec: print(r)
print(veh.to_string()); print(M["sim"])
