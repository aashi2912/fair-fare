import duckdb
con=duckdb.connect('nyc.duckdb')
print('Airport pickups Sunday Nov 30 2025, 3pm-midnight, by app')
for r in con.execute("""select app, count(*), round(median(w),1), round(avg(CASE WHEN w>10 THEN 100.0 ELSE 0 END),1), round(median(f),2)
 from nov where pu in (1,132,138) and dt='2025-11-30' and hr>=15 group by 1""").fetchall(): print(r)
con.execute("""CREATE OR REPLACE TABLE sep AS SELECT CASE hvfhs_license_num WHEN 'HV0003' THEN 'Uber' WHEN 'HV0005' THEN 'Lyft' END app,
 cast(request_datetime as date) dt, hour(request_datetime) hr, dayofweek(request_datetime) dow,
 date_diff('second',request_datetime,on_scene_datetime)/60.0 w, PULocationID pu, DOLocationID do_, trip_miles mi, trip_time tt,
 base_passenger_fare f, driver_pay p, tips tip
 FROM 'fhvhv_2026-09.parquet' WHERE hvfhs_license_num IN ('HV0003','HV0005') AND shared_request_flag='N' AND on_scene_datetime IS NOT NULL""")
con.execute("DELETE FROM sep WHERE w<0 OR w>60 OR f<=0 OR mi<=0 OR tt<=0")
print('Sep 2026 raw:', con.execute("select app,count(*),round(median(f),2),round(median(w),1),round(sum(p)/sum(f)*100,1) from sep group by 1").fetchall())
# matched cells: same pickup zone, dropoff zone, hour, weekday/weekend
con.execute("""CREATE OR REPLACE TABLE cells AS select pu, do_, hr, (dow in (0,6)) wk, app, count(*) n, median(f) mf, median(f/mi) fpm, median(w) mw,
 avg(CASE WHEN w>10 THEN 1.0 ELSE 0 END) p10, sum(p) sp, sum(f) sf, median(mi) mmi
 from sep group by all""")
q="""with m as (select u.pu,u.do_,u.hr,u.wk, u.n un, l.n ln, u.mf umf, l.mf lmf, u.mw umw, l.mw lmw, u.p10 up, l.p10 lp, u.sp/u.sf ushare, l.sp/l.sf lshare, u.mmi umi, l.mmi lmi
 from cells u join cells l using(pu,do_,hr,wk) where u.app='Uber' and l.app='Lyft' and u.n>=20 and l.n>=20)
 select count(*) cells, sum(un+ln) trips,
 round(sum((umf/lmf-1)*(un+ln))/sum(un+ln)*100,1) uber_fare_premium_pct,
 round(sum(CASE WHEN umf>lmf THEN un+ln ELSE 0 END)/sum(un+ln)*100,1) pct_trips_where_uber_pricier,
 round(sum((umw-lmw)*(un+ln))/sum(un+ln),2) uber_wait_diff_min,
 round(sum((up-lp)*(un+ln))/sum(un+ln)*100,2) uber_p10_diff_pts,
 round(sum(ushare*(un+ln))/sum(un+ln)*100,1) uber_driver_share, round(sum(lshare*(un+ln))/sum(un+ln)*100,1) lyft_driver_share,
 round(sum((umi/lmi-1)*(un+ln))/sum(un+ln)*100,1) dist_diff_pct
 from m"""
print('Matched (same pickup zone, dropoff zone, hour, weekday/weekend):')
print(con.execute(q).df().T)
