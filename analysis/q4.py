import duckdb
con=duckdb.connect('nyc.duckdb', read_only=True)
q="""with m as (select u.hr, u.n un, l.n ln, u.mf umf, l.mf lmf, u.p10 up, l.p10 lp
 from cells u join cells l using(pu,do_,hr,wk) where u.app='Uber' and l.app='Lyft' and u.n>=20 and l.n>=20)
 select CASE WHEN hr between 0 and 4 THEN '0-4 late night' WHEN hr between 5 and 9 THEN '5-9 morning' WHEN hr between 10 and 15 THEN '10-15 midday' ELSE '16-23 evening' END band,
 round(sum((umf/lmf-1)*(un+ln))/sum(un+ln)*100,1) uber_premium, round(sum(CASE WHEN umf>lmf THEN un+ln ELSE 0 END)/sum(un+ln)*100,0) pct_uber_pricier,
 round(sum((up-lp)*(un+ln))/sum(un+ln)*100,1) uber_longwait_pts, round(avg(up)*100,1) uber_p10, round(avg(lp)*100,1) lyft_p10, sum(un+ln) trips
 from m group by 1 order by 1"""
print(con.execute(q).df().to_string())
# median-of-ratios robustness
print(con.execute("""select round(median(u.mf/l.mf),3) med_ratio from cells u join cells l using(pu,do_,hr,wk) where u.app='Uber' and l.app='Lyft' and u.n>=20 and l.n>=20""").fetchall())
