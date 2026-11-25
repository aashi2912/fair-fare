import duckdb
con=duckdb.connect('nyc.duckdb', read_only=True)
print('Airport pickups, Sundays 3pm-midnight: by app, TG Sunday vs normal Sundays; long-wait share and fare/mile of long vs quick')
q="""with s as (select app, CASE WHEN dt='2025-11-30' THEN 'TG' ELSE 'norm' END d, CASE WHEN dt='2025-11-30' THEN 1 ELSE 3 END nd, w, f/mi fpm
 from nov where pu in (1,132,138) and hr>=15 and dt in ('2025-11-09','2025-11-16','2025-11-23','2025-11-30') and mi>=0.5)
select app, d, round(count(*)/any_value(nd)) per_day, round(avg(CASE WHEN w>10 THEN 100.0 ELSE 0 END),1) pct10,
 round(median(CASE WHEN w>10 THEN fpm END),2) fpm_long, round(median(CASE WHEN w<=5 THEN fpm END),2) fpm_quick, round(median(fpm),2) fpm_all
from s group by 1,2 order by 1,2"""
print(con.execute(q).df().to_string())
print('Wednesday Nov 26, 4am hour, to airports, same check')
q2="""with s as (select app, CASE WHEN dt='2025-11-26' THEN 'TG' ELSE 'norm' END d, w, f/mi fpm from nov where do_ in (1,132,138) and hr=4 and dt in ('2025-11-05','2025-11-12','2025-11-19','2025-11-26'))
select app, d, count(*) n, round(avg(CASE WHEN w>10 THEN 100.0 ELSE 0 END),1) pct10, round(median(CASE WHEN w>10 THEN fpm END),2) fpm_long, round(median(CASE WHEN w<=5 THEN fpm END),2) fpm_quick from s group by 1,2 order by 1,2"""
print(con.execute(q2).df().to_string())
