import duckdb
con=duckdb.connect(); con.execute("SET memory_limit='4GB'; SET threads=2")
months=['2025-10','2025-11','2025-12','2026-01','2026-02','2026-03','2026-04','2026-05','2026-06','2026-07','2026-08','2026-09']
for m in months:
    con.execute(f"""CREATE OR REPLACE TABLE c AS SELECT CASE hvfhs_license_num WHEN 'HV0003' THEN 'Uber' ELSE 'Lyft' END app,
     PULocationID pu, DOLocationID do_, hour(request_datetime) hr, dayofweek(request_datetime) in (0,6) wk, count(*) n, median(base_passenger_fare) mf
     FROM 'fhvhv_{m}.parquet' WHERE hvfhs_license_num IN ('HV0003','HV0005') AND shared_request_flag='N' AND on_scene_datetime IS NOT NULL
       AND date_diff('second',request_datetime,on_scene_datetime) BETWEEN 0 AND 300 AND base_passenger_fare>0 AND trip_miles>0 GROUP BY ALL""")
    r=con.execute("""with m as (select u.n un, l.n ln, u.mf umf, l.mf lmf from c u join c l using(pu,do_,hr,wk) where u.app='Uber' and l.app='Lyft' and u.n>=20 and l.n>=20)
     select sum(un+ln), round(sum((umf/lmf-1)*(un+ln))/sum(un+ln)*100,1), round(sum(CASE WHEN umf>lmf THEN un+ln ELSE 0 END)*100.0/sum(un+ln),1) from m""").fetchone()
    print(m, r, flush=True)
