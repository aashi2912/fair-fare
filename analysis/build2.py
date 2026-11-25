import duckdb, time
t=time.time()
con=duckdb.connect('year.duckdb')
con.execute("SET memory_limit='4GB'; SET threads=2; SET preserve_insertion_order=false")
con.execute("""CREATE OR REPLACE TABLE samp AS SELECT app, mon, dow, hr, pu, do_, w, eng, mi, f, p, tip FROM trips
 WHERE w BETWEEN 0 AND 60 AND f>0 AND mi>0 AND eng>0 AND eng<300 USING SAMPLE 3 PERCENT (bernoulli)""")
print('sample', con.execute('select count(*) from samp').fetchall(), round(time.time()-t))
