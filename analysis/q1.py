import duckdb
con=duckdb.connect('nyc.duckdb', read_only=True)
q="""select app, d, hb, round(n/nd) per_day, medwait, pct10, medfare, per_mile from (
 select app, CASE WHEN dt='2025-11-26' THEN 'TG' ELSE 'norm' END d, CASE WHEN dt='2025-11-26' THEN 1 ELSE 3 END nd, (hr//3)*3 hb,
 count(*) n, round(median(w),1) medwait, round(avg(CASE WHEN w>10 THEN 100.0 ELSE 0 END),1) pct10, round(median(f),2) medfare, round(median(f/mi),2) per_mile
 from nov where do_ in (1,132,138) and dt in ('2025-11-05','2025-11-12','2025-11-19','2025-11-26') group by 1,2,3,4) order by 1,3,2"""
print('app, day, hourblock, trips/day, median wait, %>10min, median fare, fare/mile')
for r in con.execute(q).fetchall(): print(r)
