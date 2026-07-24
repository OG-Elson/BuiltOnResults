import importlib, search_api as s, json, hashlib, os, re, csv, urllib.parse
importlib.reload(s)

MARKET="africa"; DEPTH=30; CACHE="/home/deploy/builtonresults/.serp_cache"
KW="cleaning services mombasa"
BLOCK=("facebook.","instagram.","linkedin.","tripadvisor.","yelp.","google.","youtube.","twitter.","x.com",
 "jiji.","pigiame","brabys","businesslist.","yellowpages","myjobmag","directory.","mymrmedia","kenyabizlist",
 "tiktok.","mombasappliances")  # mombasappliances = appareils, hors sujet
PROB={'HTTPS':"Pas de HTTPS (non sécurisé)",'Mobile viewport':"Pas optimisé mobile",
 'Meta description':"Meta description absente/faible",'Keyword in title':"Mot-clé absent du <title>",
 'Structured data (schema)':"Aucune donnée structurée (schema)",'Content depth (300+ words)':"Contenu trop maigre",
 'Single H1 heading':"H1 manquant/multiple",'Title tag present':"Balise <title> absente",
 'Title length (30-65)':"Longueur de title non optimale",'Image alt coverage':"Images sans alt"}
ORDER={k:i for i,k in enumerate(['HTTPS','Mobile viewport','Meta description','Keyword in title','Structured data (schema)','Content depth (300+ words)','Single H1 heading','Title tag present','Title length (30-65)','Image alt coverage'])}

existing=set(r['domaine'] for r in csv.DictReader(open('/home/deploy/vault/projects/builtonresults/prospects_cote_mombasa.csv')))

cf=os.path.join(CACHE,hashlib.md5(f"{KW}|{MARKET}|{DEPTH}".encode()).hexdigest()+".json")
items=json.load(open(cf))
cands=[]
for it in items:
    if it.get('type')!='organic': continue
    r=it.get('rank_group') or 0
    dom=(it.get('domain') or '').lower().replace('www.','')
    if not (4<=r<=30): continue
    if not dom or dom in existing or any(b in dom for b in BLOCK): continue
    cands.append((r,dom,it.get('url') or 'https://'+dom))

def wa_num(phone):
    if not phone: return None
    d=re.sub(r'\D','',phone)
    if d.startswith('0') and len(d)==10: d='254'+d[1:]
    elif d.startswith('7') and len(d)==9: d='254'+d
    elif d.startswith('1') and len(d)==9: d='254'+d
    # doit être 254 + 9 chiffres, préfixe MOBILE (7 ou 1) — exclut fixes (20/41) et numéros cassés
    if len(d)==12 and d.startswith('254') and d[3] in '71':
        return d
    return None

BAD_TITLES={'home','welcome','index','untitled','menu','loading','page'}
def biz_name(title,dom):
    if title:
        t=re.split(r'[|\-–—:•·]',title)[0].strip()
        tl=t.lower()
        bad=(tl in BAD_TITLES or 'cleaning services' in tl or 'best cleaning' in tl
             or 'mombasa county' in tl or 'company in mombasa' in tl or len(t)>32 or len(t)<3)
        if not bad: return t
    return "there"  # greeting sûr plutôt qu'un nom faux

def msg(name,pos):
    # Angle conversationnel : AUCUN lien (évite la preview WhatsApp), pas de pitch/prix, finit sur une question ouverte.
    who=name if name!="there" else "there"
    return (f"Hi {who} 👋 I came across your site while looking at cleaning companies in Mombasa. "
      f'Quick honest note: when someone here searches "cleaning services mombasa", you\'re showing up around '
      f"#{pos} — so most of those customers are landing on the companies above you and calling them, not you.\n\n"
      "Getting local businesses to the top of Google — and giving them a site that actually turns visitors into "
      "bookings — is basically what I do. I recently took a Diani business here from invisible to #1.\n\n"
      "Would you be open to me sending you a quick example of what that could look like for your business? "
      "No pressure at all 🙂\n— Elson")

rows=[]
for pos,dom,url in sorted(cands):
    try: pg=s.crawl_page(url,KW)
    except Exception: pg={'crawled':False}
    probs=[]; email=phone=None; title=None
    if pg.get('crawled'):
        title=pg.get('title')
        sc=s.scorecard_checks(pg) or {}
        fails=sorted([c['k'] for c in sc.get('checks',[]) if not c['ok']], key=lambda k:ORDER.get(k,99))
        probs=[PROB.get(k,k) for k in fails[:3]]
        phone=pg.get('phone_found')
        m=re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', pg.get('body_excerpt','') or '')
        if m: email=m.group(0)
    else: probs=["Site inaccessible/lent (déjà un signal à vendre)"]
    name=biz_name(title,dom); wn=wa_num(phone)
    rows.append({'name':name,'dom':dom,'pos':pos,'probs':probs,'email':email,'phone':phone,'wa':wn,'msg':msg(name,pos)})

# écriture markdown
out=["# Cleaning Mombasa — BATCH 2 (angle conversationnel, sans lien)\n",
     f"> {len(rows)} prospects · message court & humain, **aucun lien** (évite la preview WhatsApp) · finit sur une question ouverte.\n",
     "> ⚠️ N'envoie PAS le showcase dans le 1er message. **Quand ils répondent « oui »** → là tu envoies : https://builtonresults.co.ke/showcase/cleaning-mombasa + proposes le mini-audit gratuit.\n",
     "> Espace les envois (numéro neuf).\n"]
for r in rows:
    out.append(f"\n## {r['pos']:>2}. {r['name']}  ({r['dom']})")
    out.append(f"⚠️ {' · '.join(r['probs'])}")
    out.append(f"📇 {r['email'] or ''}{' / ' if r['email'] and r['phone'] else ''}{r['phone'] or ''}".strip(' /') or "📇 (contact à trouver sur le site)")
    if r['wa']:
        out.append(f"👉 Envoyer : https://wa.me/{r['wa']}?text="+urllib.parse.quote(r['msg']))
    else:
        out.append("👉 Pas de mobile WhatsApp détecté → email/appel, ou copie le message ci-dessous.")
    out.append(f"\n<details><summary>message</summary>\n\n{r['msg']}\n\n</details>")
open('/home/deploy/builtonresults/outreach/cleaning_batch2.md','w').write('\n'.join(out))
print(f"✅ {len(rows)} prospects cleaning batch 2 → outreach/cleaning_batch2.md")
for r in rows:
    print(f"  #{r['pos']:>2} {r['dom']:32} wa={'oui' if r['wa'] else 'NON':3} | {r['probs'][0][:40]}")
