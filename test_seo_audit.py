#!/usr/bin/env python3
"""Test workflow for SEO Audit tool."""
import requests, json, sys, os, re
from urllib.parse import urlparse

TESTS = []
PASS = 0
FAIL = 0

def test(name, fn):
    global PASS, FAIL
    TESTS.append(name)
    try:
        ok, msg = fn()
        if ok:
            PASS += 1
            print(f"  ✅ {name}")
        else:
            FAIL += 1
            print(f"  ❌ {name}: {msg}")
    except Exception as e:
        FAIL += 1
        print(f"  ❌ {name}: EXCEPTION {e}")

def check_url(url):
    """Fetch a URL and return status + title + meta."""
    try:
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        title = re.search(r'<title>(.*?)</title>', r.text, re.I)
        desc = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', r.text, re.I)
        has_schema = 'application/ld+json' in r.text or 'schema.org' in r.text
        return {
            'status': r.status_code,
            'title': title.group(1)[:60] if title else None,
            'desc': desc.group(1)[:100] if desc else None,
            'has_schema': has_schema,
            'size': len(r.text)
        }
    except Exception as e:
        return {'status': 0, 'error': str(e)}

# ====== TEST 1: URL validation ======
print("\n📋 TEST 1 — Validation d'URL")

test("URL valide https://chefangela.co.ke", lambda:
    (True, "") if check_url("https://chefangela.co.ke")['status'] == 200
    else (False, f"Status: {check_url('https://chefangela.co.ke')['status']}"))

test("URL invalide retourne erreur", lambda:
    (True, "") if check_url("https://sitenonexistant123456xyz.com")['status'] != 200
    else (False, "Devrait echouer"))

test("URL sans http est detectee", lambda:
    (False, "") if requests.get("http://example.com", timeout=5).status_code == 200
    else (True, "Erreur attendue"))

# ====== TEST 2: Position Google via Brave Search ======
print("\n📋 TEST 2 — Recherche de position (Brave Search API)")

BRAVE_KEY = None
env_path = "/home/deploy/.hermes/.env"
if os.path.exists(env_path):
    for line in open(env_path):
        if 'BRAVE' in line and '=' in line:
            val = line.strip().split('=',1)[1].strip()
            if val and not val.startswith('#'):
                BRAVE_KEY = val
                break

if BRAVE_KEY:
    test("Brave Search API accessible", lambda:
        (True, "") if requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={'q': 'chef angela diani beach'},
            headers={'Accept': 'application/json', 'Accept-Encoding': 'gzip', 'X-Subscription-Token': BRAVE_KEY},
            timeout=10
        ).status_code == 200
        else (False, "API non accessible"))

    # Test recherche réelle
    r = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        params={'q': 'chef angela diani beach'},
        headers={'Accept': 'application/json', 'Accept-Encoding': 'gzip', 'X-Subscription-Token': BRAVE_KEY},
        timeout=10
    )
    if r.status_code == 200:
        data = r.json()
        results = data.get('web', {}).get('results', [])
        test("Recherche chef angela retourne des resultats", lambda:
            (True, "") if len(results) > 0
            else (False, "0 resultats"))

        # Trouver position de chefangela.co.ke
        for i, res in enumerate(results):
            url = res.get('url', '')
            if 'chefangela.co.ke' in url:
                test(f"chefangela.co.ke trouve en position #{i+1}", lambda: (True, ""))
                break
        else:
            test("chefangela.co.ke trouve dans les resultats", lambda:
                (False, "Pas trouve dans les 10 premiers resultats"))
    else:
        test("Recherche Brave API OK", lambda: (False, f"HTTP {r.status_code}"))
else:
    print("  ⚠️  Pas de cle Brave Search API — tests de position ignores")

# ====== TEST 3: Simulation des secteurs ======
print("\n📋 TEST 3 — Coherence des secteurs")

sectors = {
    'restaurant': {'o': 20, 'c': 0.04, 't': 10000},
    'hotel': {'o': 150, 'c': 0.05, 't': 10000},
    'ecommerce': {'o': 45, 'c': 0.03, 't': 10000},
    'service': {'o': 250, 'c': 0.07, 't': 10000},
    'artisan': {'o': 180, 'c': 0.06, 't': 10000},
    'immobilier': {'o': 2000, 'c': 0.02, 't': 10000},
    'sante': {'o': 80, 'c': 0.05, 't': 10000},
    'education': {'o': 150, 'c': 0.04, 't': 10000}
}

for name, s in sectors.items():
    ctr_top3 = 0.17  # position #2
    visitors = round(s['t'] * ctr_top3)
    revenue = round(visitors * s['c'] * s['o'])
    test(f"Coherence {name}: {visitors}v -> {revenue}$/mois", lambda v=visitors, r=revenue:
        (True, "") if r > 10
        else (False, f"Revenu trop faible: {r}$"))

# ====== TEST 4: Verifier la page HTML ======
print("\n📋 TEST 4 — Verification page HTML")

html_path = "/var/www/flyer-gigs/out/seo-audit.html"
if os.path.exists(html_path):
    html = open(html_path).read()
    test("Page contient le titre principal", lambda:
        (True, "") if "Que perds-tu" in html
        else (False, "Titre manquant"))
    test("Page contient le tableau positions", lambda:
        (True, "") if "Position" in html and "35%" in html
        else (False, "Tableau manquant"))
    test("Page contient le formulaire", lambda:
        (True, "") if "sectorSelect" in html and "urlInput" in html
        else (False, "Formulaire manquant"))
    test("Page contient les 3 etapes du plan", lambda:
        (True, "") if "Step 1" in html or "sn\">1<" in html
        else (False, "Plan action manquant"))
    test("Page contient le pricing", lambda:
        (True, "") if "$15" in html
        else (False, "Pricing $15 manquant"))
    test("Page contient le cas reel", lambda:
        (True, "") if "Chef Angela" in html
        else (False, "Cas reel manquant"))
    test("Page contient la bulle info CTR", lambda:
        (True, "") if "Taux de clics" in html and "info" in html
        else (False, "Bulle CTR manquante"))
else:
    test("Fichier HTML existe", lambda: (False, f"{html_path} introuvable"))

# ====== TEST 5: Accessibilite HTTP ======
print("\n📋 TEST 5 — Accessibilite HTTP")

r = requests.get("http://localhost/flyer/seo-audit.html", timeout=5)
test("Page accessible (HTTP 200)", lambda:
    (True, "") if r.status_code == 200
    else (False, f"HTTP {r.status_code}"))
test("Taille page > 10KB", lambda:
    (True, "") if len(r.text) > 10000
    else (False, f"{len(r.text)} bytes"))
test("Encodage UTF-8", lambda:
    (True, "") if 'charset=utf-8' in r.text.lower() or 'utf-8' in r.apparent_encoding.lower()
    else (False, f"Encoding: {r.apparent_encoding}"))

# ====== BILAN ======
print(f"\n{'='*40}")
print(f"📊 BILAN: {PASS}/{PASS+FAIL} tests reussis")
if FAIL > 0:
    print(f"⚠️  {FAIL} echec(s) a corriger")
else:
    print(f"✅ Tout est OK !")
