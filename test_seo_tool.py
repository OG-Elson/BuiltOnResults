#!/usr/bin/env python3
"""
SEO Audit tool — REAL test workflow (supersedes test_workflow_client.py).

Unlike the previous script (which only checked plumbing and never validated a
single computed number), this one:

  A. BACKEND     — asserts the API contract, cache, graceful error handling,
                   rate limiting, and market handling (few real calls).
  B. CALCULATION — parses the REAL mkt/ctr constants from the HTML, replicates
                   the render() formula, and asserts the numbers a client sees
                   (this is where the previous "report" invented figures).
  C. SECURITY    — asserts user input is escaped before innerHTML (no DOM XSS).
  D. FRONT-END   — headless smoke: the page renders, no template leaks.

Run:  python3 test_seo_tool.py
Exit: 0 = all green, 1 = failure(s).
"""
import subprocess, sys, os, json, re, time, urllib.request, urllib.error, urllib.parse

HOST = "46.224.49.147"
BASE = "http://127.0.0.1"
API = f"{BASE}/flyer/api/search"
# Test the FIXED editorial version (preview). The live /flyer/seo-audit.html is the OLD design.
HTML_FILE = "/home/deploy/builtonresults/seo-audit.html"
PAGE_URL = f"{BASE}/flyer/seo-audit-preview.html"
CHROME = os.path.expanduser("~/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome")

P = F = 0
def ok(msg):
    global P; P += 1; print(f"  \033[32m✅\033[0m {msg}")
def ko(msg):
    global F; F += 1; print(f"  \033[31m❌ {msg}\033[0m")
def head(t): print(f"\n\033[1m{t}\033[0m")

MOCK = os.environ.get("MOCK") == "1"   # MOCK=1 → no real API calls (backend/rate-limit use canned data, 0 budget)
_mock_seen = set()
def api(q, site, m="global", timeout=15):
    if MOCK:
        key = (q, site, m); cached = key in _mock_seen; _mock_seen.add(key)
        found = "chefangela" in site
        return 200, {"position": 4 if found else None, "found": found,
                     "source": "Google (DataForSEO)", "count": 1 if found else 0, "cost": 0, "cached": cached}
    url = f"{API}?q={urllib.parse.quote(q)}&site={urllib.parse.quote(site)}&m={m}"
    req = urllib.request.Request(url, headers={"Host": HOST})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode())

# ─────────────────────────────────────────────────────────────
head("A. BACKEND — API contract, cache, error handling, rate limit" + (" [MOCK — canned data, 0 budget]" if MOCK else ""))

REQUIRED = {"position", "found", "source"}
try:
    st, d = api("private chef diani", "chefangela.co.ke")
    ok("API returns HTTP 200") if st == 200 else ko(f"HTTP {st}")
    ok("Response is valid JSON with required fields") if REQUIRED <= set(d) else ko(f"missing fields: {REQUIRED - set(d)}")
    ok(f"Known site resolves to a real Google position (#{d.get('position')}, source={d.get('source')})") \
        if d.get("found") and isinstance(d.get("position"), int) else ko(f"no real position: {d}")
except Exception as e:
    ko(f"API call failed: {e}")

# Cache: identical 2nd call must be served from cache
try:
    _, d2 = api("private chef diani", "chefangela.co.ke")
    ok("Cache works (2nd identical call served from cache)") if d2.get("cached") else ko("2nd call not cached")
except Exception as e:
    ko(f"cache test failed: {e}")

# Error handling: a malformed/garbage site must still return valid JSON (never a 500/empty body)
try:
    st, d = api("zzq test", "%%%not-a-url%%%")
    valid = st == 200 and isinstance(d, dict) and "found" in d
    ok("Malformed input still returns valid JSON (found=false, no crash)") if valid else ko(f"bad response: {st} {d}")
except Exception as e:
    ko(f"error-handling test failed (got exception instead of JSON): {e}")

# Markets: each market must be accepted and return valid JSON (africa must NOT be a US location)
try:
    # ONE real call on a non-default market (spares the 5/min limit); the rest checked statically.
    st, d = api("seo services", "example.com", m="africa")
    ok("Non-default market (africa) accepted, valid JSON") if st == 200 and "found" in d else ko(f"africa market failed: {st}")
    page = open(HTML_FILE, encoding="utf-8").read()
    have_all = all(f'value="{mk}"' in page for mk in ["global", "eu", "us", "africa", "asia"])
    ok("All 5 market options present in the page") if have_all else ko("a market option missing from HTML")
    # africa location code check (backend source): must be Kenya (2404), not US (2840)
    src = open("/home/deploy/builtonresults/search_api.py").read()
    m = re.search(r"'africa':\s*(\d+)", src)
    ok("Backend: 'africa' market → Kenya (2404), not US") if m and m.group(1) == "2404" else ko(f"africa code = {m and m.group(1)} (expected 2404)")
except Exception as e:
    ko(f"market test failed: {e}")

# Rate limiting: a rapid burst must be throttled (429 from the app AND/OR 503 from nginx limit_req).
head("A2. Rate limiting (rapid burst must be throttled)")
try:
    if MOCK:
        codes = [200, 429, 503, 503, 503]  # canned (proven live behaviour); no API calls in mock
    else:
        codes = []
        for i in range(9):
            try:
                st, _ = api(f"rl probe {i}", "example.com", timeout=8)
                codes.append(st)
            except urllib.error.HTTPError as he:
                codes.append(he.code)
            except Exception as e:
                codes.append(f"ERR:{type(e).__name__}")
    n200 = codes.count(200)
    blocked = codes.count(429) + codes.count(503)
    ok(f"Rate limiting enforced (burst throttled): {n200} allowed / {blocked} blocked — codes={codes}") \
        if blocked >= 1 and n200 <= 6 else ko(f"rate limit weak/absent: codes={codes}")
except Exception as e:
    ko(f"rate limit test failed: {e}")

# ─────────────────────────────────────────────────────────────
head("B. CALCULATION — the numbers a client actually sees")
# Parse the REAL mkt/ctr constants from the HTML and replicate render()'s formula in Node.
node_script = r'''
const fs=require('fs');
const html=fs.readFileSync(process.argv[2],'utf8');
const mm=html.match(/const mkt=(\{[\s\S]*?\});\s*const ctr=(\{[^;]*\});/);
if(!mm){console.error('could not extract mkt/ctr from HTML');process.exit(2);}
const mkt=eval('('+mm[1]+')');
const ctr=eval('('+mm[2]+')');
// Replicated exactly from render(): tr=t*ctr[p]; t3=t*0.17; g=t3-tr; m=g*c*o
function calc(sector,market,pos){
  const sd=mkt[market][sector];
  const tr=Math.round(sd.t*(ctr[pos]||.01));
  const t3=Math.round(sd.t*ctr[1]);
  const g=Math.max(0,t3-tr);
  const m=Math.round(g*sd.c*sd.o);
  return {t:sd.t,visitors:tr,gainVisitors:g,gainRevenue:m,cur:mkt[market].sym};
}
const out={fail:[],info:{}};
function assert(cond,msg){ if(!cond) out.fail.push(msg); }

// 1) The report's scenario: service / global / #2 → prove the real output
const r=calc('service','global',2);
out.info.reportScenario=r;
assert(r.visitors===Math.round(600*0.17), `service/global/#2 visitors should be ~102, got ${r.visitors}`);
assert(r.gainRevenue>0 && r.gainRevenue<2000, `service/global/#2 gain toward #1 should be a modest positive, got $${r.gainRevenue}`);

// 2) Target = position #1 (ctr[1]=0.35). A #1 site shows $0; worse positions show a monotonically larger gain.
const disp=(s,mk,p)=>calc(s,mk,p).gainRevenue;
assert(disp('service','global',1)===0, 'pos #1 should show $0 (already #1)');
assert(disp('service','global',2)>0, 'pos #2 should show a positive gain toward #1');
assert(disp('service','global',4)>disp('service','global',2), 'a worse position should show a larger gain toward #1');
out.info.pos1IsZero=disp('service','global',1)===0;
// 3) Monotonic: worse position (higher number) → >= gain than a better one (for pos>3)
assert(calc('service','global',10).gainRevenue >= calc('service','global',5).gainRevenue,
  'gain should not decrease as position worsens');
// 4) Sanity bounds: no single-keyword monthly gain should exceed a sane ceiling
let maxGain=0, worst='';
for(const market of Object.keys(mkt)) for(const sector of Object.keys(mkt.global)){
  if(sector==='sym'||sector==='r') continue;
  for(const pos of Object.keys(ctr)){
    const g=calc(sector,market,+pos).gainRevenue;
    if(g>maxGain){maxGain=g; worst=`${sector}/${market}/#${pos}`;}
  }
}
out.info.maxGain={value:maxGain,where:worst};
assert(maxGain < 20000, `implausible max monthly gain $${maxGain} at ${worst} (>$20k from ONE keyword)`);
// 5) Currency per market matches config
assert(calc('service','eu',5).cur==='€', 'EU market should use € symbol');

// 6) DISCREPANCY: static reference table (1,700 for #2) vs sector calculator (t=600 → 102)
out.info.staticTableSaysPos2 = 1700;
out.info.calculatorSaysPos2  = calc('service','global',2).visitors;
console.log(JSON.stringify(out));
'''
try:
    with open("/tmp/_seo_logic.js", "w") as f:
        f.write(node_script)
    res = subprocess.run(["node", "/tmp/_seo_logic.js", HTML_FILE], capture_output=True, text=True, timeout=30)
    if res.returncode != 0:
        ko(f"logic test node error: {res.stderr[:300]}")
    else:
        out = json.loads(res.stdout.strip().splitlines()[-1])
        r = out["info"]["reportScenario"]
        print(f"     → REAL tool output for the report's client (service/global/#2): "
              f"{r['visitors']} visitors/mo, +${r['gainRevenue']}/mo gain")
        print(f"     → Static reference table says #2 = {out['info']['staticTableSaysPos2']} visits "
              f"vs calculator = {out['info']['calculatorSaysPos2']} visits  (INCONSISTENT by design)")
        print(f"     → Max possible monthly gain across all sectors/markets: "
              f"${out['info']['maxGain']['value']} at {out['info']['maxGain']['where']}")
        print(f"     → Model = potential at #1: #1 shows $0, worse positions grow toward #1 (pos1IsZero={out['info']['pos1IsZero']}).")
        if out["fail"]:
            for msg in out["fail"]:
                ko(msg)
        else:
            ok("Calculation invariants hold (formula matches, #1 = $0, monotonic, bounds sane, currency per market)")
        # The old Hermes report claimed 1,700 visits / $25,200 gain for this scenario — neither matches the tool.
        ok(f"CONFIRMED: old report's '1,700 visits / $25,200' does NOT match tool output "
           f"({out['info']['calculatorSaysPos2']} visits / +${r['gainRevenue']}/mo)") \
            if out["info"]["calculatorSaysPos2"] != 1700 and r['gainRevenue'] < 5000 else ko("report numbers unexpectedly matched")
except Exception as e:
    ko(f"calculation test failed: {e}")

# ─────────────────────────────────────────────────────────────
head("C. SECURITY — user input escaped before innerHTML (no DOM XSS)")
html = open(HTML_FILE, encoding="utf-8").read()
ok("esc() helper present") if "const esc=s=>String(s).replace" in html else ko("esc() helper missing")
ok("URL escaped for display (uShow)") if "${uShow}" in html else ko("URL not escaped in render()")
ok("Keyword escaped for display (kwE)") if "🔑 ${kwE}" in html and 'explain1(p,kwE,' in html else ko("keyword not escaped in render()")
# no RAW keyword/url interpolated directly into the result badges/heading
raw_sink = re.search(r'🔑 \$\{kw\}|"\$\{kw\}"\$\{foundPages', html)
ok("No raw ${kw}/${u} left in the result innerHTML sinks") if not raw_sink else ko("raw XSS sink still present")

# ─────────────────────────────────────────────────────────────
head("D. FRONT-END — headless render smoke")
try:
    r = subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--dump-dom",
                        "--virtual-time-budget=4000", PAGE_URL],
                       capture_output=True, text=True, timeout=40)
    dom = r.stdout
    ok("Page renders in headless Chromium") if "SEO Audit Express" in dom else ko("page did not render")
    ok("Calculator form present (urlInput)") if "urlInput" in dom else ko("form missing")
    ok("Result container present (#result)") if 'id="result"' in dom else ko("#result missing")
    # No premature render: #result must be empty until the user clicks Calculate
    ok("No premature render (#result empty on load)") if re.search(r'id="result">\s*</div>', dom) else ko("#result not empty on load")
except Exception as e:
    ko(f"headless smoke failed: {e}")

# ─────────────────────────────────────────────────────────────
print(f"\n{'='*56}")
print(f"\033[1mRESULT: {P}/{P+F} checks passed\033[0m")
if F:
    print(f"\033[31m⚠️  {F} failure(s) — see above.\033[0m")
    print("NOTE: this validates PLUMBING + CALCULATION CONSISTENCY only.")
    print("      Business-data realism (search volumes, avg order, conversion) is a")
    print("      separate content decision and is NOT certified here.")
    sys.exit(1)
else:
    print("\033[32m✅ Plumbing solid + calculation consistent with the formula.\033[0m")
    print("⚠️  Business-data realism (volumes/order/conv) still to validate — NOT 'client-ready' by itself.")
    sys.exit(0)
