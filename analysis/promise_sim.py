"""Cost of a monthly cap on Uber's share of rider payments, simulated on NYC TLC trips (Sep 2026).

TLC data has no driver IDs, so trips are grouped into synthetic driver-months of 160 trips
under three assumptions about how drivers work: a typical mix of trips, sticking to one
pickup area, or one area and the same hours. Real drivers sit somewhere in between, so the
scenarios bracket the cost rather than measure it. Platform share = (base fare - driver pay)
/ base fare, both before tips, tolls, taxes and fees. NYC has a driver pay floor, so shares
and costs elsewhere are likely higher.

Usage: python promise_sim.py fhvhv_2026-09.parquet ../promise/sim.json
"""
import sys, json
import duckdb, numpy as np

src, dst = sys.argv[1], sys.argv[2]
con = duckdb.connect(); con.execute("SET memory_limit='5GB'; SET threads=2")
con.execute(f"""CREATE TABLE t AS SELECT PULocationID z, hour(request_datetime) h, base_passenger_fare f, driver_pay p, random() r
 FROM '{src}' WHERE hvfhs_license_num='HV0003' AND shared_request_flag='N' AND base_passenger_fare>2 AND driver_pay>0""")
dist = con.execute("""SELECT least(19,greatest(0,floor((least(greatest((f-p)/f,-0.2),0.7999)+0.2)/0.05)))::INT b, count(*) FROM t GROUP BY 1 ORDER BY 1""").fetchall()
tot = sum(c for _, c in dist)
hist = [{"lo": round(-0.2 + b * 0.05, 2), "hi": round(-0.2 + (b + 1) * 0.05, 2), "pct": round(100 * c / tot, 2)} for b, c in dist]
stats = con.execute("""SELECT count(*), round(100*sum(f-p)/sum(f),1), round(100*avg(CASE WHEN (f-p)/f>0.40 THEN 1 ELSE 0 END),1), round(100*avg(CASE WHEN p>=f THEN 1 ELSE 0 END),1) FROM t""").fetchone()
N = 160
out = {"month": "2026-09", "trips": stats[0], "overall_share": stats[1], "pct_trips_over40": stats[2], "pct_trips_zero_or_less": stats[3], "trips_per_driver_month": N, "hist": hist, "scenarios": {}}
for key, label, order in [('mixed', 'Each driver gets a typical mix of trips', 'r'), ('area', 'Drivers stick to one area', 'z, r'), ('area_hour', 'Drivers stick to one area and the same hours', 'z, h, r')]:
    arr = np.array(con.execute(f"""WITH g AS (SELECT (row_number() OVER (ORDER BY {order}))//{N} d, f, p FROM t)
      SELECT sum(f), sum(p) FROM g GROUP BY d HAVING count(*)={N}""").fetchall(), dtype=float)
    f, p = arr[:, 0], arr[:, 1]; fee = f - p; share = fee / f; total_fee = fee.sum()
    rows = []
    for cap in range(20, 51):
        c = cap / 100; over = share > c; top = np.maximum(0, fee - c * f)
        rows.append({"cap": cap, "pct_driver_months": round(100 * over.mean(), 2), "cost_pct_fees": round(100 * top.sum() / total_fee, 3), "avg_topup": round(float(top[over].mean()) if over.any() else 0, 2)})
    out["scenarios"][key] = {"label": label, "driver_months": int(len(f)), "p90_share": round(100 * float(np.percentile(share, 90)), 1), "max_share": round(100 * float(share.max()), 1), "rows": rows}
json.dump(out, open(dst, 'w'), indent=0)
