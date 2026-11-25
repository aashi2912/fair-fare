import duckdb
con=duckdb.connect('nyc.duckdb')
#con.execute("""CREATE OR REPLACE TABLE nov AS SELECT CASE hvfhs_license_num WHEN 'HV0003' THEN 'Uber' WHEN 'HV0005' THEN 'Lyft' END app,
 request_datetime rq, cast(request_datetime as date) dt, hour(request_datetime) hr, date_diff('second',request_datetime,on_scene_datetime)/60.0 w, PULocationID pu, DOLocationID do_,
 trip_miles mi, base_passenger_fare f, driver_pay p
 FROM 'fhvhv_2025-11.parquet' WHERE hvfhs_license_num IN ('HV0003','HV0005') AND shared_request_flag='N' AND on_scene_datetime IS NOT NULL""")
con.execute("DELETE FROM nov WHERE w<0 OR w>60 OR f<=0 OR mi<=0")
q="""select app, d, hb, round(n/nd) per_day, medwait, pct10, medfare, per_mile from (
 select app, CASE WHEN dt='2025-11-26' THEN 'TG' ELSE 'norm' END d, CASE WHEN dt='2025-11-26' THEN 1 ELSE 3 END nd, (hr//3)*3 hb,
 count(*) n, round(median(w),1) medwait, round(avg(CASE WHEN w>10 THEN 100.0 ELSE 0 END),1) pct10, round(median(f),2) medfare, round(median(f/mi),2) per_mile
 from nov where do_ in (1,132,138) and dt in ('2025-11-05','2025-11-12','2025-11-19','2025-11-26') group by 1,2,3,4) order by 1,3,2"""
for r in con.execute(q).fetchall(): print(r)
