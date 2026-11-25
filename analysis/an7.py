import duckdb
con=duckdb.connect(); con.execute("SET memory_limit='4GB'; SET threads=2")
for app,code in [('Uber','HV0003'),('Lyft','HV0005')]:
  for m in ['2025-10','2026-09']:
    con.execute(f"""CREATE OR REPLACE TABLE t AS SELECT PULocationID pu, DOLocationID do_, hour(request_datetime) hr, dayofweek(request_datetime) in (0,6) wk,
      date_diff('second',request_datetime,on_scene_datetime)/60.0 w, base_passenger_fare f
      FROM 'fhvhv_{m}.parquet' WHERE hvfhs_license_num='{code}' AND shared_request_flag='N' AND on_scene_datetime IS NOT NULL AND base_passenger_fare>0 AND trip_miles>0""")
    r=con.execute("""with q as (select pu,do_,hr,wk, median(f) qf, count(*) n from t where w between 0 and 5 group by all having count(*)>=15)
      select count(*) long_trips,
       round(avg(CASE WHEN f < 0.85*qf THEN 100.0 ELSE 0 END),1) pct_15pct_cheaper,
       round(avg(CASE WHEN f > 1.15*qf THEN 100.0 ELSE 0 END),1) pct_15pct_pricier,
       round(median(f/qf),3) med_ratio
      from t join q using(pu,do_,hr,wk) where w>10 and w<=60""").fetchall()
    base=con.execute("""with q as (select pu,do_,hr,wk, median(f) qf from t where w between 0 and 5 group by all having count(*)>=15)
      select round(avg(CASE WHEN f < 0.85*qf THEN 100.0 ELSE 0 END),1) from t join q using(pu,do_,hr,wk) where w between 0 and 5""").fetchone()
    print(app, m, 'long-wait trips (n, % >=15% cheaper than quick median, % >=15% pricier, median ratio):', r, '| quick trips that are >=15% cheaper (baseline):', base)
