#!/usr/bin/env python3
"""Test pipeline — compare positions across search engines."""
import json, os, urllib.request, gzip, re, sys
from urllib.parse import urlparse, quote

BRAVE_KEY = None
env_path = os.path.expanduser("~/.hermes/.env")
if os.path.exists(env_path):
    for line in open(env_path):
        if 'BRAVE_API_KEY' in line and '=' in line:
            val = line.strip().split('=', 1)[1].strip().replace('"', '')
            if val and not val.startswith('#'):
                BRAVE_KEY = val
                break

def extract_domain(url):
    domain = urlparse(url).netloc if '://' in url else url
    return re.sub(r'^www\.', '', domain).lower()

def search_brave(query, site):
    if not BRAVE_KEY:
        return {'error': 'No Brave API key'}
    try:
        url = f"https://api.search.brave.com/res/v1/web/search?q={quote(query)}&count=20"
        req = urllib.request.Request(url)
        req.add_header('Accept-Encoding', 'gzip')
        req.add_header('X-Subscription-Token', BRAVE_KEY)
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read()
            if r.headers.get('Content-Encoding') == 'gzip': raw = gzip.decompress(raw)
            data = json.loads(raw)
        results = data.get('web', {}).get('results', [])
        domain = extract_domain(site)
        positions = [i+1 for i, res in enumerate(results) if domain in res.get('url', '')]
        return {'positions': positions, 'best': min(positions) if positions else None, 'count': len(positions)}
    except Exception as e:
        return {'error': str(e)}

def search_duckduckgo(query, site):
    """Search via DuckDuckGo HTML."""
    domain = extract_domain(site)
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode()
        # Extract result URLs from DuckDuckGo HTML
        links = re.findall(r'class="result__url"[^>]*href="([^"]*)"', html)
        if not links:
            links = re.findall(r'class="result__a"[^>]*href="([^"]*)"', html)
        if not links:
            # Try alternate pattern
            links = re.findall(r'<a[^>]*class="[^"]*result[^"]*"[^>]*href="([^"]*)"', html)
        positions = [i+1 for i, link in enumerate(links) if domain in link.lower()]
        return {'positions': positions[:5], 'best': min(positions) if positions else None, 'count': len(positions)}
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    queries = [
        ('aestus resort kenya', 'https://www.aestusresortkenya.com/'),
        ('private chef diani', 'https://chefangela.co.ke'),
        ('hotel diani beach', 'https://www.aestusresortkenya.com/'),
    ]
    
    print("=" * 60)
    print("TEST PIPELINE — Comparaison des positions par moteur")
    print("=" * 60)
    
    for query, site in queries:
        print(f"\n🔍 Query: \"{query}\"")
        print(f"   Site: {site}")
        print("-" * 40)
        
        # Brave
        brave = search_brave(query, site)
        if 'error' in brave:
            print(f"   ❌ Brave API: {brave['error']}")
        else:
            print(f"   ✅ Brave API: best position #{brave['best']} ({brave['count']} pages found)")
        
        # DuckDuckGo
        ddg = search_duckduckgo(query, site)
        if 'error' in ddg:
            print(f"   ❌ DuckDuckGo: {ddg['error']}")
        else:
            print(f"   ✅ DuckDuckGo: best position #{ddg['best']} ({ddg['count']} pages found)")
        
        # Compare
        brave_pos = brave.get('best') if 'best' in brave else None
        ddg_pos = ddg.get('best') if 'best' in ddg else None
        
        if brave_pos and ddg_pos:
            diff = abs(brave_pos - ddg_pos)
            if diff <= 1:
                print(f"   ✅ Coherence: gap de {diff} position(s)")
            else:
                print(f"   ⚠️ Ecart: {diff} positions entre Brave et DuckDuckGo")
        elif brave_pos or ddg_pos:
            print(f"   ℹ️ Un seul resultat disponible")
        else:
            print(f"   ❌ Aucun resultat disponible")
    
    print("\n" + "=" * 60)
    print("TEST TERMINE — Verifie les ecarts ci-dessus")
    print("=" * 60)
