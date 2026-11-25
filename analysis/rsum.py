import duckdb
con=duckdb.connect('routes.duckdb', read_only=True)
con.execute("CREATE TEMP TABLE z AS SELECT * FROM read_csv_auto('zones.csv')")
base="""select *, (un+ln) wt, uqf/lqf ratio from pair where uqf is not null and lqf is not null and unq>=15 and lnq>=15"""
print('== Overall (Jul-Sep 2026): trip-weighted Uber price vs Lyft on quick-pickup rides, share of trips where each is cheaper by 5%+')
print(con.execute(f"""with p as ({base}) select count(*) routes, sum(wt) trips, round((sum(ratio*wt)/sum(wt)-1)*100,1) uber_vs_lyft_pct,
 round(sum(CASE WHEN ratio<0.95 THEN wt END)*100.0/sum(wt),1) uber_cheaper5, round(sum(CASE WHEN ratio>1.05 THEN wt END)*100.0/sum(wt),1) lyft_cheaper5,
 round(sum(u10*wt)/sum(wt),1) uber_long, round(sum(l10*wt)/sum(wt),1) lyft_long from p""").df().to_string())
print('== By time band')
print(con.execute(f"""with p as ({base}) select band, wk, sum(wt) trips, round((sum(ratio*wt)/sum(wt)-1)*100,1) uber_vs_lyft_pct,
 round(sum(u10*wt)/sum(wt),1) uber_long, round(sum(l10*wt)/sum(wt),1) lyft_long from p group by 1,2 order by 2,1""").df().to_string())
print('== By pickup borough')
print(con.execute(f"""with p as ({base}) select z.Borough, sum(wt) trips, round((sum(ratio*wt)/sum(wt)-1)*100,1) uber_vs_lyft_pct,
 round(sum(u10*wt)/sum(wt),1) uber_long, round(sum(l10*wt)/sum(wt),1) lyft_long from p join z on z.LocationID=p.pu group by 1 order by 2 desc""").df().to_string())
print('== Airport rides (to or from JFK/LGA/EWR)')
print(con.execute(f"""with p as ({base}) select CASE WHEN do_ in (1,132,138) THEN 'to airport' ELSE 'from airport' END dir, sum(wt) trips, round((sum(ratio*wt)/sum(wt)-1)*100,1) uber_vs_lyft_pct,
 round(sum(u10*wt)/sum(wt),1) uber_long, round(sum(l10*wt)/sum(wt),1) lyft_long from p where pu in (1,132,138) or do_ in (1,132,138) group by 1""").df().to_string())
print('== By trip length')
print(con.execute(f"""with p as ({base}) select CASE WHEN miles<2 THEN 'a <2mi' WHEN miles<5 THEN 'b 2-5mi' WHEN miles<10 THEN 'c 5-10mi' ELSE 'd 10+mi' END len, sum(wt) trips, round((sum(ratio*wt)/sum(wt)-1)*100,1) uber_vs_lyft_pct,
 round(sum(u10*wt)/sum(wt),1) uber_long, round(sum(l10*wt)/sum(wt),1) lyft_long from p group by 1 order by 1""").df().to_string())
