import duckdb
con=duckdb.connect('year.duckdb', read_only=True); con.execute("SET memory_limit='4GB'")
print('== Monthly long-wait % by app, and mean wait')
print(con.execute("""select mon, round(sum(CASE WHEN app='Uber' THEN n10 END)*100.0/sum(CASE WHEN app='Uber' THEN n END),2) uber10,
 round(sum(CASE WHEN app='Lyft' THEN n10 END)*100.0/sum(CASE WHEN app='Lyft' THEN n END),2) lyft10,
 round(sum(CASE WHEN app='Uber' THEN sw END)/sum(CASE WHEN app='Uber' THEN n END),2) uber_mean_w,
 round(sum(CASE WHEN app='Lyft' THEN sw END)/sum(CASE WHEN app='Lyft' THEN n END),2) lyft_mean_w,
 round(sum(CASE WHEN app='Uber' THEN n END)/1e6,2) uber_m, round(sum(CASE WHEN app='Lyft' THEN n END)/1e6,2) lyft_m
 from agg group by 1 order by 1""").df().to_string())
print('== Wait distribution in sample: Oct 2025 vs Sep 2026, Uber')
print(con.execute("""select mon, app, round(avg(CASE WHEN w<=5 THEN 100.0 ELSE 0 END),1) le5, round(avg(CASE WHEN w>5 and w<=10 THEN 100.0 ELSE 0 END),1) b5_10,
 round(avg(CASE WHEN w>10 and w<=20 THEN 100.0 ELSE 0 END),1) b10_20, round(avg(CASE WHEN w>20 and w<=40 THEN 100.0 ELSE 0 END),1) b20_40, round(avg(CASE WHEN w>40 THEN 100.0 ELSE 0 END),2) gt40,
 round(median(w),2) med from samp where mon in ('2025-10','2026-09') group by 1,2 order by 2,1""").df().to_string())
