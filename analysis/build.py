import duckdb, time
t=time.time()
con=duckdb.connect('year.duckdb')
con.execute("SET memory_limit='20GB'")
con.execute("""CREATE OR REPLACE VIEW trips AS SELECT
 CASE hvfhs_license_num WHEN 'HV0003' THEN 'Uber' ELSE 'Lyft' END app,
 strftime(request_datetime,'%Y-%m') mon, dayofweek(request_datetime) dow, hour(request_datetime) hr,
 PULocationID pu, DOLocationID do_,
 date_diff('second',request_datetime,on_scene_datetime)/60.0 w,
 date_diff('second',request_datetime,dropoff_datetime)/60.0 eng,
 trip_miles mi, trip_time/60.0 tt, base_passenger_fare f, driver_pay p, tips tip
 FROM read_parquet('fhvhv_20*.parquet')
 WHERE hvfhs_license_num IN ('HV0003','HV0005') AND shared_request_flag='N' AND on_scene_datetime IS NOT NULL
   AND request_datetime >= '2025-10-01' AND request_datetime < '2026-10-01'""")
con.execute("""CREATE OR REPLACE TABLE agg AS SELECT app, mon, dow, hr, pu,
 count(*) n, sum(CASE WHEN w>10 THEN 1 ELSE 0 END) n10, sum(CASE WHEN w>5 THEN 1 ELSE 0 END) n5, sum(w) sw,
 sum(p) sp, sum(tip) stip, sum(f) sf, sum(eng) seng, sum(mi) smi, sum(tt) stt
 FROM trips WHERE w BETWEEN 0 AND 60 AND f>0 AND mi>0 AND eng>0 AND eng<300 GROUP BY ALL""")
print('agg rows', con.execute('select count(*), sum(n) from agg').fetchall(), round(time.time()-t))
# hourly wait distribution medians (exact) per app & hour
con.execute("""CREATE OR REPLACE TABLE hourmed AS SELECT app, hr, (dow in (0,6)) wk, median(w) medw, quantile_cont(w,0.9) p90w,
 median((p+tip)/eng*60) med_rate FROM trips WHERE w BETWEEN 0 AND 60 AND f>0 AND mi>0 AND eng>0 AND eng<300 GROUP BY ALL""")
print('done', round(time.time()-t))
