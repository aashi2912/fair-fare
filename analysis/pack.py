import duckdb, json, csv
con=duckdb.connect('routes.duckdb', read_only=True)
bands=['early','am_rush','midday','pm_rush','evening','late']
zones=[]
for r in csv.DictReader(open('zones.csv')):
    i=int(r['LocationID'])
    if r['Borough'] in ('Unknown','N/A') or i>263: continue
    zones.append([i, r['Zone'], r['Borough']])
zb={z[0]:z[2] for z in zones}
rows=con.execute("""select pu, do_, band, wk::int, round(uqf,1), round(lqf,1), round(u10,1), round(l10,1), un+ln
 from pair where uqf is not null and lqf is not null and unq>=15 and lnq>=15""").fetchall()
out=[]
for pu,do,b,wk,uf,lf,u10,l10,n in rows:
    if pu not in zb or do not in zb: continue
    out.append([pu,do,bands.index(b),wk,uf,lf,u10,l10,int(n)])
# borough-level fallback (weighted)
con.execute("CREATE TEMP TABLE z AS SELECT LocationID id, Borough b FROM read_csv_auto('zones.csv')")
bor=con.execute("""select zp.b, zd.b, band, wk::int, round(sum(uqf/lqf*(un+ln))/sum(un+ln),4), round(sum(u10*(un+ln))/sum(un+ln),1), round(sum(l10*(un+ln))/sum(un+ln),1), sum(un+ln)
 from pair join z zp on zp.id=pu join z zd on zd.id=do_ where uqf is not null and lqf is not null and unq>=15 and lnq>=15 and zp.b not in ('Unknown','N/A') and zd.b not in ('Unknown','N/A') group by all""").fetchall()
bor=[[a,b,bands.index(c),d,e,f,g,int(h)] for a,b,c,d,e,f,g,h in bor]
data={'zones':zones,'bands':bands,'rows':out,'bor':bor}
s=json.dumps(data,separators=(',',':'))
open('/home/claude/whichapp/data.json','w').write(s)
print(len(out),'rows', len(bor),'borough rows', round(len(s)/1e6,2),'MB')
