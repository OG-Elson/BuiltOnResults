import importlib, search_api as s, urllib.request, json, re, csv, sys, os, hashlib
importlib.reload(s)

MARKET="africa"
SECTORS = {
 'legal':      ["law firms in mombasa","lawyers in mombasa"],
 'dental':     ["dental clinic mombasa"],
 'cleaning':   ["cleaning services mombasa"],
 'architects': ["architects in mombasa"],
 'pest':       ["pest control mombasa"],
}
QUOTA = {'legal':6,'dental':5,'cleaning':5,'architects':5,'pest':4}

# faux positifs : annuaires, médias, social, ordres pro, cabinets mondiaux, data companies
BLOCK = ("facebook.","instagram.","linkedin.","tripadvisor.","yelp.","google.","goo.gl","youtube.",
 "twitter.","x.com","maps.","glassdoor","indeed.","wikipedia.","businesslist.","yellowpages","yellow.place",
 "jiji.","pigiame","brabys","cybo.","tuugo.","2findlocal","cylex","hotfrog","n49.","opendi.","vymaps",
 "kenyaplex","storeboard","expat.com","clutch.","designrush","goodfirms","sortlist","m.facebook",
 # noise repéré au run 1
 "dentons.com","bestlawyers.com","lawyer254.com","mls.or.ke","rentechdigital.com","majira.co.ke",
 "trustpilot","bizcommunity",".gov.",".go.ke")

CACHE_DIR="/home/deploy/builtonresults/.serp_cache"; os.makedirs(CACHE_DIR, exist_ok=True)
def serp_items(keyword, depth=30):
    k=hashlib.md5(f"{keyword}|{MARKET}|{depth}".encode()).hexdigest(); cf=os.path.join(CACHE_DIR,k+".json")
    if os.path.exists(cf):
        print(f"  [cache] {keyword}", file=sys.stderr); return json.load(open(cf))
    loc=s.LOCATION_CODES.get(MARKET,2404)
    payload=json.dumps([{"keyword":keyword,"location_code":loc,"language_code":"en","depth":depth}]).encode()
    req=urllib.request.Request(s.API_URL,data=payload); req.add_header('Authorization',f'Basic {s.AUTH_BASE64}'); req.add_header('Content-Type','application/json')
    try: data=json.loads(urllib.request.urlopen(req,timeout=30).read()); items=data['tasks'][0]['result'][0].get('items',[])
    except Exception as e: print(f"  [err] {keyword}: {e}",file=sys.stderr); items=[]
    json.dump(items, open(cf,'w')); print(f"  [FETCH ${'%.3f'%(data.get('cost',0) if 'data' in dir() else 0)}] {keyword}", file=sys.stderr)
    return items

PROB={'HTTPS':("Pas de HTTPS (non sécurisé)",1),'Mobile viewport':("Pas optimisé mobile",2),
 'Meta description':("Meta description absente/faible",3),'Keyword in title':("Mot-clé absent du <title>",4),
 'Structured data (schema)':("Aucune donnée structurée (schema)",5),'Content depth (300+ words)':("Contenu trop maigre",6),
 'Single H1 heading':("H1 manquant/multiple",7),'Title tag present':("Balise <title> absente",8),
 'Title length (30-65)':("Longueur de title non optimale",9),'Image alt coverage':("Images sans alt",10)}

def collect(seeds):
    seen=set(); res=[]
    for kw in seeds:
        for it in serp_items(kw):
            if it.get('type')!='organic': continue
            rank=it.get('rank_group') or 0
            if not (11<=rank<=30): continue
            dom=(it.get('domain') or '').lower().replace('www.',''); url=it.get('url') or ''
            if not dom or dom in seen or any(b in dom for b in BLOCK): continue
            seen.add(dom); res.append({'kw':kw,'pos':rank,'domain':dom,'url':url})
    return res

out=[]
for sector, seeds in SECTORS.items():
    cands=collect(seeds); picked=cands[:QUOTA[sector]]
    print(f">>> {sector}: {len(cands)} candidats → {len(picked)} retenus", file=sys.stderr)
    for r in picked:
        try: pg=s.crawl_page(r['url'],r['kw'])
        except Exception: pg={'crawled':False}
        probs=[]; email=phone=None
        if pg.get('crawled'):
            sc=s.scorecard_checks(pg) or {}
            fails=sorted([c['k'] for c in sc.get('checks',[]) if not c['ok']], key=lambda k:PROB.get(k,('',99))[1])
            probs=[PROB.get(k,(k,99))[0] for k in fails[:3]]
            phone=pg.get('phone_found')
            m=re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', pg.get('body_excerpt','') or '')
            if m: email=m.group(0)
        else: probs=["Site inaccessible/lent"]
        contact=" / ".join([x for x in [email,phone] if x]) or "(voir site)"
        top=probs[0] if probs else "problèmes on-page"; p2=probs[1] if len(probs)>1 else ""
        acc=(f"Hi — you're #{r['pos']} on Google for '{r['kw']}'. Quick free audit of {r['domain']}: "
             f"{top}{(', '+p2) if p2 else ''}. Likely why competitors above you get the calls. Want the full report — free?")
        out.append({'secteur':sector,'domaine':r['domain'],'position':r['pos'],'mot_cle':r['kw'],
          'probleme_1':probs[0] if probs else '','probleme_2':probs[1] if len(probs)>1 else '',
          'probleme_3':probs[2] if len(probs)>2 else '','contact':contact,'accroche':acc})

path="/home/deploy/builtonresults/prospects_cote_mombasa.csv"
with open(path,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['secteur','domaine','position','mot_cle','probleme_1','probleme_2','probleme_3','contact','accroche']); w.writeheader(); w.writerows(out)
print(f"\n=== {len(out)} PROSPECTS (diversifiés) → {path} ===")
cur=None
for o in out:
    if o['secteur']!=cur: cur=o['secteur']; print(f"\n──── {cur.upper()} ────")
    print(f"#{o['position']:>2} {o['domaine']:32} ⚠️ {o['probleme_1']} | {o['probleme_2']} | {o['probleme_3']}")
    print(f"     📇 {o['contact']}")
