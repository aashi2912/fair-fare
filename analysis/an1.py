import duckdb
con=duckdb.connect('year.duckdb', read_only=True)
con.execute("SET memory_limit='4GB'")
print('== Year totals')
print(con.execute("select app, sum(n), round(sum(n10)*100.0/sum(n),2) pct10, round(sum(sp)/sum(sf)*100,1) drv_share, round((sum(sp)+sum(stip))/sum(seng)*60,2) rate_per_eng_hr, round(sum(stip)/sum(sp)*100,1) tip_pct from agg group by 1").df().to_string())
print('== By hour (weekdays Mon-Fri), both apps: volume/day, long-wait %, driver $/engaged hr, $/mile, avg trip miles')
df=con.execute("""select hr, round(sum(n)/261.0) trips_per_day, round(sum(n10)*100.0/sum(n),1) pct10,
 round(sum(CASE WHEN app='Uber' THEN n10 END)*100.0/sum(CASE WHEN app='Uber' THEN n END),1) uber10,
 round(sum(CASE WHEN app='Lyft' THEN n10 END)*100.0/sum(CASE WHEN app='Lyft' THEN n END),1) lyft10,
 round((sum(sp)+sum(stip))/sum(seng)*60,2) rate, round(sum(sp)/sum(smi),2) per_mile, round(sum(smi)/sum(n),1) avg_mi, round(sum(sw)/sum(n),1) mean_wait
 from agg where dow between 1 and 5 group by 1 order by 1""").df()
print(df.to_string())
print('corr(pct10, rate) weekday hours:', round(df['pct10'].corr(df['rate']),2), ' corr(pct10, trips):', round(df['pct10'].corr(df['trips_per_day']),2))
print('== By month: long-wait % and volume')
print(con.execute("select mon, round(sum(n)/1e6,2) m_trips, round(sum(n10)*100.0/sum(n),2) pct10, round((sum(sp)+sum(stip))/sum(seng)*60,2) rate from agg group by 1 order by 1").df().to_string())
