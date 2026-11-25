import duckdb
con=duckdb.connect(); con.execute("SET memory_limit='4GB'; SET threads=2")
for m in ['2025-10','2026-03','2026-09']:
    con.execute(f"""CREATE OR REPLACE TABLE c AS SELECT PULocationID pu, DOLocationID do_, hour(request_datetime) hr, dayofweek(request_datetime) in (0,6) wk,
     CASE WHEN w>10 THEN 'long' WHEN w<=5 THEN 'quick' END k, count(*) n, median(base_passenger_fare) mf, median(w) mw, median(trip_miles) mm
     FROM (SELECT *, date_diff('second',request_datetime,on_scene_datetime)/60.0 w FROM 'fhvhv_{m}.parquet'
       WHERE hvfhs_license_num='HV0003' AND shared_request_flag='N' AND on_scene_datetime IS NOT NULL AND base_passenger_fare>0 AND trip_miles>0)
     WHERE w BETWEEN 0 AND 60 AND (w>10 OR w<=5) GROUP BY ALL""")
    df=con.execute("""select q.n qn, l.n ln, q.mf-l.mf saved, l.mw-q.mw extra, q.mf qf, q.mm qm, l.mm lm
      from c q join c l using(pu,do_,hr,wk) where q.k='quick' and l.k='long' and q.n>=15 and l.n>=15""").df()
    df['w']=df.qn+df.ln
    import numpy as np
    df=df[df.extra>0]
    per_min=(df.saved/df.extra)
    def wmed(x,w):
        o=np.argsort(x.values); c=np.cumsum(w.values[o]); return x.values[o][np.searchsorted(c,c[-1]/2)]
    print(m, 'cells',len(df),'trips',int(df.w.sum()),
      '| median $ saved per long-wait ride', round(wmed(df.saved,df.w),2),
      '| median extra wait min', round(wmed(df.extra,df.w),1),
      '| $/min', round(wmed(per_min,df.w),2), '| implied $/hr', round(wmed(per_min,df.w)*60,1),
      '| saving as % of quick fare', round(wmed(df.saved/df.qf*100,df.w),1),
      '| distance ratio long/quick', round(wmed(df.lm/df.qm,df.w),3))
