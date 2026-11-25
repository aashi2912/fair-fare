import duckdb
con=duckdb.connect('nyc.duckdb', read_only=True)
print('TO airports, hourly 2am-9am, Uber+Lyft combined: TG Wed (Nov 26) vs normal Weds (Nov 5,12,19)')
q="""select hr, d, round(n/nd) per_day, medwait, pct10, medfare from (
 select hr, CASE WHEN dt='2025-11-26' THEN 'TG' ELSE 'norm' END d, CASE WHEN dt='2025-11-26' THEN 1 ELSE 3 END nd,
 count(*) n, round(median(w),1) medwait, round(avg(CASE WHEN w>10 THEN 100.0 ELSE 0 END),1) pct10, round(median(f),2) medfare
 from nov where do_ in (1,132,138) and hr between 2 and 9 and dt in ('2025-11-05','2025-11-12','2025-11-19','2025-11-26') group by 1,2,3) order by 1,2"""
for r in con.execute(q).fetchall(): print(r)
print('FROM airports (pickups at JFK/LGA/EWR), Sunday Nov 30 vs normal Sundays (Nov 9,16,23), 3-hour blocks')
q="""select hb, d, round(n/nd) per_day, medwait, pct10, medfare from (
 select (hr//3)*3 hb, CASE WHEN dt='2025-11-30' THEN 'TG Sun' ELSE 'norm' END d, CASE WHEN dt='2025-11-30' THEN 1 ELSE 3 END nd,
 count(*) n, round(median(w),1) medwait, round(avg(CASE WHEN w>10 THEN 100.0 ELSE 0 END),1) pct10, round(median(f),2) medfare
 from nov where pu in (1,132,138) and dt in ('2025-11-09','2025-11-16','2025-11-23','2025-11-30') group by 1,2,3) order by 1,2"""
for r in con.execute(q).fetchall(): print(r)
print('Which days of TG week were busiest to airports?')
for r in con.execute("select dt, dayname(dt), count(*) , round(avg(CASE WHEN w>10 THEN 100.0 ELSE 0 END),1) from nov where do_ in (1,132,138) and dt between '2025-11-21' and '2025-11-30' group by 1,2 order by 1").fetchall(): print(r)
