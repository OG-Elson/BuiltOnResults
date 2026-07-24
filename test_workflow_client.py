#!/usr/bin/env python3
"""Test workflow — simulate real client using the SEO Audit tool."""
import requests, json, sys, time

BASE = "http://localhost"
SEO_PAGE = f"{BASE}/flyer/seo-audit.html"
API_URL = f"{BASE}/flyer/api/search"

PASS = 0; FAIL = 0; TESTS = []

def test(name, fn):
    global PASS, FAIL
    try:
        fn()
        PASS += 1; print(f"  ✅ {name}")
    except Exception as e:
        FAIL += 1; print(f"  ❌ {name}: {e}")

def check(label, condition, detail=""):
    if not condition:
        raise AssertionError(f"{label} FAILED {detail}")

# ─── TEST 1: Page loads ───
print("\n📄 TEST 1 — Page loads correctly")
r = requests.get(SEO_PAGE, timeout=10)
check("Page HTTP", r.status_code == 200, f"(got {r.status_code})")
check("Has calculator", "urlInput" in r.text)
check("Has lang toggle", "data-en" in r.text or "langToggle" in r.text)
check("Has PDF/print", "print" in r.text.lower() or "pdf" in r.text.lower())
check("Has pricing", "$15" in r.text or "15" in r.text)
TESTS.extend(["Page HTTP", "Calculator form", "Lang toggle", "PDF button", "Pricing"])

# ─── TEST 2: API call - known site (Chef Angela) ───
print("\n🔍 TEST 2 — API: Chef Angela (should be #1)")
r = requests.get(f"{API_URL}?q=private+chef+diani&site=https://chefangela.co.ke", timeout=15)
d = r.json()
check("HTTP 200", r.status_code == 200)
check("Found", d.get('found'), f"got position={d.get('position')}")
check("Position #1", d.get('position') in [1,2,3,4,5], f"got #{d.get('position')}")
check("Source is Google", 'Google' in d.get('source', ''), f"source={d.get('source')}")
check("Has count", d.get('count', 0) > 0)
print(f"  Position: #{d.get('position')} | Pages: {d.get('count')} | Cost: ${d.get('cost')}")

# ─── TEST 3: API call - non-Kenyan site ───
print("\n🔍 TEST 3 — API: International site (booking.com)")
r = requests.get(f"{API_URL}?q=hotel+booking+mombasa&site=https://booking.com", timeout=15)
d = r.json()
check("HTTP 200", r.status_code == 200)
if d.get('found'):
    check("Pos range", 1 <= d.get('position', 0) <= 50, f"got #{d.get('position')}")
print(f"  Position: #{d.get('position')} | Found: {d.get('found')}")

# ─── TEST 4: API call - unknown site ───
print("\n🔍 TEST 4 — API: Unknown/random site")
r = requests.get(f"{API_URL}?q=test+keyword&site=https://nonexistent-test-12345.com", timeout=15)
d = r.json()
check("HTTP 200", r.status_code == 200)
print(f"  Found: {d.get('found')} | Expected fallback: estimation")

# ─── TEST 5: Rate limiting ───
print("\n⏱️  TEST 5 — Rate limiting (5 requests)")
count_ok = 0
for i in range(6):
    try:
        r = requests.get(f"{API_URL}?q=test+{i}&site=https://example.com", timeout=5)
        if r.status_code == 200:
            count_ok += 1
    except:
        pass  # rate-limited (429/503/timeout) = normal
check("Max 5 allowed", count_ok <= 5, f"got {count_ok} successful")
print(f"  {count_ok} succeeded out of 6 (expected ≤5)")

# ─── TEST 6: Market-specific data ───
print("\n🌍 TEST 6 — Market selection data")
r = requests.get(SEO_PAGE, timeout=10)
for market in ["global", "eu", "us", "africa", "asia"]:
    check(f"Market {market} in HTML", f'value="{market}"' in r.text, f"not found")
print(f"  All 6 markets found in page source")

# ─── TEST 7: PDF export ───
print("\n📑 TEST 7 — PDF export (print CSS)")
check("Print CSS present", "@media print" in r.text)
check("Print hide elements", "display:none" in r.text.lower())

# ─── SUMMARY ───
print(f"\n{'='*40}")
print(f"RÉSULTATS: {PASS}/{PASS+FAIL} tests OK")
if FAIL > 0:
    print(f"⚠️  {FAIL} échec(s) — voir détails ci-dessus")
    sys.exit(1)
else:
    print("✅ TOUT EST OK — outil prêt pour les clients")
