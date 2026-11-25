import duckdb, time
t=time.time()
con=duckdb.connect('routes.duckdb'); con.execute("SET memory_limit='4GB'; SET threads=2")
band="""CASE WHEN hr BETWEEN 4 AND 6 THEN 'early' WHEN hr BETWEEN 7 AND 9 THEN 'am_rush' WHEN hr BETWEEN 10 AND 15 THEN 'midday'
 WHEN hr BETWEEN 16 AND 18 THEN 'pm_rush' WHEN hr BETWEEN 19 AND 23 THEN 'evening' ELSE 'late' END"""
con.execute("DROP TABLE IF EXISTS cm")
for i,m in enumerate(['2026-07','2026-08','2026-09']):
    sql=f"""SELECT '{m}' mon, app, pu, do_, {band} band, wk, count(*) n, sum(CASE WHEN w>10 THEN 1 ELSE 0 END) n10,
      sum(CASE WHEN w<=5 THEN 1 ELSE 0 END) nq, median(CASE WHEN w<=5 THEN f END) qf, median(w) mw, median(mi) mmi
      FROM (SELECT CASE hvfhs_license_num WHEN 'HV0003' THEN 'Uber' ELSE 'Lyft' END app, PULocationID pu, DOLocationID do_,
        hour(request_datetime) hr, dayofweek(request_datetime) in (0,6) wk, date_diff('second',request_datetime,on_scene_datetime)/60.0 w,
        base_passenger_fare f, trip_miles mi FROM 'fhvhv_{m}.parquet'
        WHERE hvfhs_license_num IN ('HV0003','HV0005') AND shared_request_flag='N' AND on_scene_datetime IS NOT NULL AND base_passenger_fare>0 AND trip_miles>0)
      WHERE w BETWEEN 0 AND 60 GROUP BY ALL"""
    con.execute(("CREATE TABLE cm AS " if i==0 else "INSERT INTO cm ")+sql)
    print(m, round(time.time()-t), flush=True)
con.execute("""CREATE OR REPLACE TABLE r AS SELECT app, pu, do_, band, wk, sum(n) n, sum(n10) n10, sum(nq) nq,
  sum(qf*nq)/nullif(sum(CASE WHEN qf IS NOT NULL THEN nq END),0) qf, sum(mw*n)/sum(n) mw, sum(mmi*n)/sum(n) mmi FROM cm GROUP BY ALL""")
con.execute("""CREATE OR REPLACE TABLE pair AS SELECT u.pu, u.do_, u.band, u.wk, u.n un, l.n ln, u.n10*100.0/u.n u10, l.n10*100.0/l.n l10,
  u.qf uqf, l.qf lqf, u.nq unq, l.nq lnq, u.mmi miles FROM r u JOIN r l USING(pu,do_,band,wk) WHERE u.app='Uber' AND l.app='Lyft' AND u.n>=30 AND l.n>=30""")
print(con.execute("select count(*), sum(un+ln) from pair").fetchall(), round(time.time()-t))
