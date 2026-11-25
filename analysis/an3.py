import duckdb
con=duckdb.connect('year.duckdb', read_only=True); con.execute("SET memory_limit='4GB'")
# Within same month, pickup zone, hour: fare per mile of long-wait (>10) vs quick (<=5) trips
q="""with s as (select app, mon, pu, hr, CASE WHEN w>10 THEN 'long' WHEN w<=5 THEN 'quick' END k, f/mi fpm, f, mi from samp where mi>=0.5),
c as (select app, mon, pu, hr, k, median(fpm) m, count(*) n from s where k is not null group by all),
j as (select a.app, a.mon, a.m/b.m r, a.n+b.n n from c a join c b using(app,mon,pu,hr) where a.k='long' and b.k='quick' and a.n>=5 and b.n>=5)
select app, mon, round(sum(r*n)/sum(n),3) long_vs_quick_fare_per_mile, sum(n) n from j group by 1,2 order by 1,2"""
print(con.execute(q).df().to_string())
