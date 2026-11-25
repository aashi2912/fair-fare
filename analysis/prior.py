import duckdb
con=duckdb.connect(); con.execute("SET memory_limit='4GB'; SET threads=2")
for m in ['2024-10','2024-12','2025-03','2025-06','2025-09']:
    w=con.execute(f"""select CASE hvfhs_license_num WHEN 'HV0003' THEN 'Uber' ELSE 'Lyft' END app,
      round(avg(CASE WHEN w>10 THEN 100.0 ELSE 0 END),2) pct10, round(median(w),2) med
      from (select hvfhs_license_num, date_diff('second',request_datetime,on_scene_datetime)/60.0 w from 'fhvhv_{m}.parquet'
        where hvfhs_license_num in ('HV0003','HV0005') and shared_request_flag='N' and on_scene_datetime is not null and base_passenger_fare>0 and trip_miles>0)
      where w between 0 and 60 group by 1 order by 1""").fetchall()
    con.execute(f"""CREATE OR REPLACE TABLE c AS SELECT CASE hvfhs_license_num WHEN 'HV0003' THEN 'Uber' ELSE 'Lyft' END app,
     PULocationID pu, DOLocationID do_, hour(request_datetime) hr, dayofweek(request_datetime) in (0,6) wk, count(*) n, median(base_passenger_fare) mf
     FROM 'fhvhv_{m}.parquet' WHERE hvfhs_license_num IN ('HV0003','HV0005') AND shared_request_flag='N' AND on_scene_datetime IS NOT NULL
       AND date_diff('second',request_datetime,on_scene_datetime) BETWEEN 0 AND 300 AND base_passenger_fare>0 AND trip_miles>0 GROUP BY ALL""")
    r=con.execute("""with m as (select u.n un, l.n ln, u.mf umf, l.mf lmf from c u join c l using(pu,do_,hr,wk) where u.app='Uber' and l.app='Lyft' and u.n>=20 and l.n>=20)
     select round(sum((umf/lmf-1)*(un+ln))/sum(un+ln)*100,1), round(sum(CASE WHEN umf>lmf THEN un+ln ELSE 0 END)*100.0/sum(un+ln),1) from m""").fetchone()
    print(m, 'waits', w, '| uber price premium on quick trips %', r, flush=True)
