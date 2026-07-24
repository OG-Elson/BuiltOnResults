#!/usr/bin/env python3
"""Search API endpoint using DataForSEO for real Google SERP data."""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, base64, urllib.request, re, time
import socket, ipaddress, subprocess, glob, tempfile, secrets, uuid, hmac, hashlib
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

# ── Pending audits (persist across payment redirect) + semi-auto payment approval ──
PENDING_AUDITS = os.path.expanduser('~/builtonresults_data/pending_audits.jsonl')
PENDING_PAYMENTS = os.path.expanduser('~/builtonresults_data/pending_payments.jsonl')
ADMIN_NOTIFY = 'elsongmaster@gmail.com'  # where payment-approval requests are sent
SITE = 'https://builtonresults.co.ke'

def _append_jsonl(path, rec):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'a') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        return True
    except Exception as e:
        print(f"⚠️  append {path}: {e}"); return False

def _find_jsonl(path, key, val):
    try:
        hit = None
        for line in open(path):
            if line.strip():
                r = json.loads(line)
                if r.get(key) == val:
                    hit = r  # keep last match
        return hit
    except Exception:
        return None

def _update_jsonl(path, key, val, patch):
    try:
        rows = [json.loads(l) for l in open(path) if l.strip()]
        for r in rows:
            if r.get(key) == val:
                r.update(patch)
        with open(path, 'w') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        return True
    except Exception as e:
        print(f"⚠️  update {path}: {e}"); return False

# ── Project briefs (funnel "prospects sans site") ──
PENDING_BRIEFS = os.path.expanduser('~/builtonresults_data/pending_briefs.jsonl')
DISCOVERY_CAL = 'https://calendly.com/dushimeelvis/discovery-call-new-project'
GUMROAD_URL = 'https://elsongster.gumroad.com/l/seo-audit'

# ── Umami analytics (server-side events for backend-only conversions) ──
UMAMI_SEND_URL = 'https://analytics.builtonresults.co.ke/api/send'
UMAMI_WEBSITE_ID = 'bf937960-b95a-4c84-b467-62f76cb830c4'
def umami_track(name, data=None):
    """Send a server-side event to Umami (best-effort — never blocks the main flow).
    Used for conversions the JS snippet can't see (paid approval, brief qualify/decline)."""
    try:
        payload = json.dumps({'type': 'event', 'payload': {
            'website': UMAMI_WEBSITE_ID, 'hostname': 'builtonresults.co.ke',
            'url': '/server-event', 'name': name, 'data': data or {}}}).encode()
        # Umami drops events from non-browser User-Agents (bot filter) — must look like a real browser.
        req = urllib.request.Request(UMAMI_SEND_URL, data=payload, headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        urllib.request.urlopen(req, timeout=5).read()
    except Exception as e:
        print(f"⚠️  umami_track error: {e}")

def _server_secret():
    """Persistent server secret for HMAC magic-link tokens (created once, outside web root)."""
    p = os.path.expanduser('~/.bor_secret')
    try:
        s = open(p).read().strip()
        if s:
            return s
    except Exception:
        pass
    s = secrets.token_hex(32)
    try:
        with open(p, 'w') as f:
            f.write(s + '\n')
        os.chmod(p, 0o600)
    except Exception:
        pass
    return s

def brief_token(bid):
    return hmac.new(_server_secret().encode(), bid.encode(), hashlib.sha256).hexdigest()[:32]

def _recent_brief(email, window=600):
    """Idempotency: same email submitted a brief in the last `window` seconds."""
    try:
        el = (email or '').lower(); now = int(time.time())
        for line in open(PENDING_BRIEFS):
            if line.strip():
                r = json.loads(line)
                if r.get('email', '').lower() == el and now - int(r.get('epoch', 0)) < window:
                    return True
    except Exception:
        pass
    return False

def read_briefs(limit=500):
    try:
        return [json.loads(l) for l in open(PENDING_BRIEFS) if l.strip()][-limit:][::-1]
    except Exception:
        return []

# ── Business config: M-Pesa hours (EAT = UTC+3, no DST) + Calendly ──
MPESA_OPEN_HOUR = 7     # 07:00 EAT
MPESA_CLOSE_HOUR = 23   # 23:00 EAT
CALENDLY_URL = "https://calendly.com/dushimeelvis/seo-strategy-call-builtonresults"

def mpesa_status():
    """Is M-Pesa manual channel open right now? (server-side EAT clock, not the client's)."""
    eat = datetime.now(timezone.utc) + timedelta(hours=3)
    h = eat.hour
    is_open = MPESA_OPEN_HOUR <= h < MPESA_CLOSE_HOUR
    if is_open:
        return {"open": True, "server_time_eat": eat.strftime("%H:%M:%S"),
                "next_open_in_seconds": None, "message": "M-Pesa payments available"}
    # seconds until next open (today 07:00 if before, else tomorrow 07:00)
    nxt = eat.replace(hour=MPESA_OPEN_HOUR, minute=0, second=0, microsecond=0)
    if h >= MPESA_CLOSE_HOUR:
        nxt = nxt + timedelta(days=1)
    return {"open": False, "server_time_eat": eat.strftime("%H:%M:%S"),
            "next_open_in_seconds": int((nxt - eat).total_seconds()),
            "message": f"M-Pesa payments closed. Reopens at {MPESA_OPEN_HOUR:02d}:00 EAT."}

def get_mpesa_number():
    """M-Pesa number lives server-side (~/.bor_mpesa) — revealed only when the channel is open."""
    try:
        for line in open(os.path.expanduser('~/.bor_mpesa')):
            line = line.strip()
            if line and not line.startswith('#'):
                return line
    except Exception:
        pass
    return 'TBD'
from urllib.parse import urlparse, parse_qs, quote
from collections import defaultdict

# Rate limiting: max 5 requests per IP per minute
RATE_LIMIT = 5
RATE_WINDOW = 60  # seconds
request_log = defaultdict(list)

# Credentials from .env (manual parsing, no dotenv dependency)
def load_env_var(key):
    """Parse .env file manually for a key."""
    env_path = os.path.expanduser('~/.hermes/.env')
    if os.path.exists(env_path):
        for line in open(env_path):
            line = line.strip()
            if line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            if k.strip() == key:
                return v.strip().strip('"\'')
    return None

AUTH_BASE64 = load_env_var('DATAFORSEO_AUTH')
if not AUTH_BASE64:
    login = load_env_var('DATAFORSEO_LOGIN')
    pwd = load_env_var('DATAFORSEO_PASSWORD')
    if login and pwd:
        AUTH_BASE64 = base64.b64encode(f"{login}:{pwd}".encode()).decode()
    else:
        AUTH_BASE64 = ''

API_URL = "https://api.dataforseo.com/v3/serp/google/organic/live/regular"
DFS_VOLUME_URL = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
DFS_RANKED_URL = "https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live"
# Shared location codes (Google): reused by SERP, search-volume and ranked-keywords calls.
LOCATION_CODES = {'global': 2840, 'eu': 2826, 'us': 2840, 'africa': 2404, 'asia': 2860}

# In-memory cache: {(query, site, market): {'result': ..., 'ts': ...}} — TTL 1h.
# Avoids repeated paid DataForSEO calls for the same audit (big latency + cost win).
CACHE_TTL = 3600  # seconds
search_cache = {}

# ── LLM analysis (paid deliverable) ──────────────────────────────────────────
# DeepSeek (OpenAI-compatible) — cheap enough for a per-audit call (~$0.0002).
# Gated behind an unlock code so the LLM only runs for PAYING clients.
DEEPSEEK_KEY = load_env_var('DEEPSEEK_API_KEY')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
# Unlock code lives OUTSIDE the web root (never served by nginx). One code per line ok.
UNLOCK_FILE = os.path.expanduser('~/.bor_unlock')
analyze_cache = {}  # (url,kw,sector,lang) -> {'result':..., 'ts':...} — avoids double-charging

def get_unlock_codes():
    """Read valid unlock codes (one per line) from the private file. Empty => disabled."""
    try:
        return {l.strip() for l in open(UNLOCK_FILE) if l.strip() and not l.startswith('#')}
    except Exception:
        return set()

# Client tracking + consultant dashboard (all OUTSIDE the web root — never served)
ADMIN_FILE = os.path.expanduser('~/.bor_admin')
AUDIT_LOG = os.path.expanduser('~/builtonresults_data/audits.jsonl')

def get_admin_codes():
    try:
        return {l.strip() for l in open(ADMIN_FILE) if l.strip() and not l.startswith('#')}
    except Exception:
        return set()

def store_audit(rec):
    try:
        os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
        with open(AUDIT_LOG, 'a') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"⚠️  store_audit error: {e}")

# Per-call DataForSEO cost ledger — every credit spent is traceable, endpoint by endpoint.
# Read a summary with:  python3 -c "import json,collections;
#   s=collections.Counter();n=collections.Counter()
#   [ (s.__setitem__(d['endpoint'],s[d['endpoint']]+d['cost']), n.__setitem__(d['endpoint'],n[d['endpoint']]+1))
#     for d in map(json.loads, open('$HOME/builtonresults_data/usage.jsonl')) ]
#   print('total $%.5f'%sum(s.values())); [print(f'  {k}: ${s[k]:.5f} ({n[k]} calls)') for k in s]"
USAGE_LOG = os.path.expanduser('~/builtonresults_data/usage.jsonl')

# ── Live DataForSEO budget counter + low-balance alert ────────────────────────
# dfs_budget.json holds the last SYNCED real balance + what we've spent since.
# Synced from the FREE user_data endpoint at startup (ground truth), then
# decremented live on every paid call. When 'remaining' drops under the warn
# threshold, we write a loud line to daemon.log + a DFS_LOW_BALANCE flag file so
# it's impossible to miss (Claude reads dfs_budget.json / the flag as pre-flight).
DFS_BUDGET_FILE = os.path.expanduser('~/builtonresults_data/dfs_budget.json')
DFS_LOW_FLAG = os.path.expanduser('~/builtonresults_data/DFS_LOW_BALANCE')

def _read_budget():
    try:
        with open(DFS_BUDGET_FILE) as f:
            return json.load(f)
    except Exception:
        return {'balance_synced': None, 'synced_ts': 0, 'spent_since_sync': 0.0,
                'remaining': None, 'warn_threshold': 0.02, 'warned': False}

def _write_budget(b):
    try:
        os.makedirs(os.path.dirname(DFS_BUDGET_FILE), exist_ok=True)
        with open(DFS_BUDGET_FILE, 'w') as f:
            json.dump(b, f)
    except Exception as e:
        print(f"⚠️  _write_budget error: {e}")

def dfs_budget_status():
    b = _read_budget()
    rem = b.get('remaining')
    if rem is None:
        return "DataForSEO budget: unknown (not synced yet)"
    return (f"DataForSEO budget: ${rem:.5f} left | synced ${b.get('balance_synced', 0):.5f}"
            f" | spent since ${b.get('spent_since_sync', 0):.5f} | warn <${b.get('warn_threshold', 0):.3f}")

def sync_dfs_balance():
    """Pull the REAL balance from DataForSEO's FREE user_data endpoint and reset the
    live counter. Called at startup so the counter always begins from ground truth."""
    if not AUTH_BASE64:
        return
    try:
        req = urllib.request.Request("https://api.dataforseo.com/v3/appendix/user_data",
                                     headers={'Authorization': f'Basic {AUTH_BASE64}',
                                              'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        res = (data.get('tasks') or [{}])[0].get('result') or [{}]
        bal = float(((res[0] or {}).get('money') or {}).get('balance') or 0)
        b = _read_budget()
        b.update({'balance_synced': round(bal, 6), 'synced_ts': round(time.time(), 1),
                  'spent_since_sync': 0.0, 'remaining': round(bal, 6),
                  'warn_threshold': round(max(0.02, bal * 0.05), 4), 'warned': False})
        _write_budget(b)
        try: os.remove(DFS_LOW_FLAG)
        except OSError: pass
        print(f"🔄 {dfs_budget_status()}")
    except Exception as ex:
        print(f"⚠️  sync_dfs_balance failed (keeping last known): {ex}")

def log_usage(endpoint, cost, meta=''):
    """Append one line per real DataForSEO call (auditable to the cent) AND decrement
    the live budget counter, raising a loud alert if we cross the low-balance threshold.
    endpoint = short label (serp/volumes/ranked); cost = USD from the API 'cost' field."""
    cost = round(float(cost or 0), 6)
    try:
        os.makedirs(os.path.dirname(USAGE_LOG), exist_ok=True)
        with open(USAGE_LOG, 'a') as f:
            f.write(json.dumps({'ts': round(time.time(), 1), 'endpoint': endpoint,
                                'cost': cost, 'meta': str(meta)[:120]}) + '\n')
    except Exception as e:
        print(f"⚠️  log_usage error: {e}")
    try:
        b = _read_budget()
        if b.get('balance_synced') is not None:
            b['spent_since_sync'] = round(b.get('spent_since_sync', 0.0) + cost, 6)
            b['remaining'] = round(b['balance_synced'] - b['spent_since_sync'], 6)
            thr = b.get('warn_threshold', 0.02)
            if b['remaining'] <= thr and not b.get('warned'):
                b['warned'] = True
                try:
                    with open(DFS_LOW_FLAG, 'w') as ff:
                        ff.write(f"LOW DataForSEO balance: ${b['remaining']:.5f} left (<= ${thr}). "
                                 f"Recharge (min $50) before more premium/prospecting calls.\n")
                except Exception: pass
                bar = "🚨" * 20
                print(f"\n{bar}\n🚨 DataForSEO LOW BALANCE: ${b['remaining']:.5f} left (threshold ${thr}).")
                print(f"🚨 Flag: {DFS_LOW_FLAG} — pause premium/prospecting until recharge.\n{bar}\n")
            _write_budget(b)
    except Exception as e:
        print(f"⚠️  budget update error: {e}")

def read_audits(limit=300):
    try:
        recs = [json.loads(l) for l in open(AUDIT_LOG) if l.strip()]
        return recs[-limit:][::-1]  # newest first
    except Exception:
        return []

# Lead capture (non-buyers) — stored, and optionally forwarded to an email automation webhook
LEADS_LOG = os.path.expanduser('~/builtonresults_data/leads.jsonl')
LEAD_WEBHOOK_FILE = os.path.expanduser('~/.bor_lead_webhook')

def store_lead(rec):
    try:
        os.makedirs(os.path.dirname(LEADS_LOG), exist_ok=True)
        with open(LEADS_LOG, 'a') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"⚠️  store_lead error: {e}")

def forward_lead(rec):
    """If a webhook URL is configured, POST the lead so an external automation can email it."""
    try:
        url = open(LEAD_WEBHOOK_FILE).read().strip()
    except Exception:
        return
    if not url.startswith('http'):
        return
    try:
        req = urllib.request.Request(url, data=json.dumps(rec).encode(),
                                     headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=8).read()
    except Exception as e:
        print(f"⚠️  forward_lead error: {e}")

def read_leads(limit=500):
    try:
        return [json.loads(l) for l in open(LEADS_LOG) if l.strip()][-limit:][::-1]
    except Exception:
        return []

def _lead_already_emailed(email, kw):
    """Idempotency for the free plan: same email + keyword already got it."""
    try:
        el = (email or '').lower()
        for line in open(LEADS_LOG):
            if line.strip():
                r = json.loads(line)
                if r.get('email', '').lower() == el and r.get('keyword', '') == kw and r.get('emailed'):
                    return True
    except Exception:
        pass
    return False

# ── Server-side PDF generation (headless Chrome) + email delivery (Brevo) ──
EMAIL_CONFIG_FILE = os.path.expanduser('~/.bor_email')

def find_chrome():
    hits = glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome'))
    return hits[0] if hits else None

def _email_config():
    """Read Brevo API key + verified sender from ~/.bor_email (KEY=..., SENDER=...)."""
    cfg = {}
    try:
        for line in open(EMAIL_CONFIG_FILE):
            line = line.strip()
            if line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            cfg[k.strip()] = v.strip()
    except Exception:
        pass
    return cfg.get('BREVO_KEY'), cfg.get('BREVO_SENDER')

def build_audit_html(a, ctx):
    """Standalone printable HTML of the paid audit (mirrors the on-screen deliverable)."""
    e = lambda s: str(s if s is not None else '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    kws = ' · '.join(e(k) for k in (a.get('long_tail_keywords') or []))
    arts = ''.join(f'<div class="art"><b>{e(c.get("title"))}</b><p>{e(c.get("why"))}</p></div>'
                   for c in (a.get('content_plan') or []))
    try:
        schema = json.dumps(a.get('schema_jsonld'), indent=2, ensure_ascii=False)
    except Exception:
        schema = str(a.get('schema_jsonld') or '')
    logo = os.path.expanduser('~/builtonresults/logo-br.png')
    logo_tag = f'<img src="file://{logo}" style="height:46px">' if os.path.exists(logo) else '<b style="font-size:1.4rem">BR</b>'
    opt = lambda label, val: (f'<div class="h">{label}</div><p>{e(val)}</p>' if val else '')
    # ── Premium: real Google search volumes (LLM long-tails priced with live data) ──
    fmt = lambda n: f'{int(n):,}' if isinstance(n, (int, float)) else '—'
    vols = a.get('keyword_volumes') or []
    if vols:
        rows = ''.join(f'<tr><td>{e(v.get("keyword"))}</td><td class="num">{fmt(v.get("volume"))}</td>'
                       f'<td class="num">{("$"+format(v.get("cpc"),".2f")) if v.get("cpc") else "—"}</td>'
                       f'<td>{e((v.get("competition") or "—").title())}</td></tr>' for v in vols)
        vol_html = ('<div class="h">Keyword demand — real Google data</div>'
                    '<table class="dt"><thead><tr><th>Keyword</th><th class="num">Searches/mo</th>'
                    '<th class="num">CPC</th><th>Competition</th></tr></thead><tbody>'
                    f'{rows}</tbody></table>')
    else:
        vol_html = f'<div class="h">Long-tail keywords</div><p>{kws}</p>'
    # ── Premium: keywords the site ALREADY ranks for (quick wins, pos 4-30) ──
    ranked = a.get('ranked_keywords') or []
    if ranked:
        rrows = ''.join(f'<tr><td>{e(rk.get("keyword"))}</td><td class="num">#{e(rk.get("position"))}</td>'
                        f'<td class="num">{fmt(rk.get("volume"))}</td></tr>' for rk in ranked)
        ranked_html = ('<div class="h">Quick wins — you already rank here (page 1-3)</div>'
                       '<p style="font-size:12px;color:#666;margin:0 0 6px">These keywords are within reach of the top 3 — '
                       'the fastest traffic gains. Prioritize them on the call.</p>'
                       '<table class="dt"><thead><tr><th>Keyword</th><th class="num">Current rank</th>'
                       '<th class="num">Searches/mo</th></tr></thead><tbody>'
                       f'{rrows}</tbody></table>')
    else:
        ranked_html = ''
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@page{{margin:1.4cm}}
body{{font-family:Arial,Helvetica,sans-serif;color:#171512;line-height:1.55;font-size:13px}}
.head{{display:flex;align-items:center;gap:14px;border-bottom:2px solid #171512;padding-bottom:12px;margin-bottom:18px}}
.t{{font-family:Georgia,serif;font-size:20px;font-weight:700}}
.sub{{font-size:11px;color:#666}}
.h{{font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:#888;margin:16px 0 4px;font-weight:700}}
code{{display:block;background:#f5f4f1;border:1px solid #ddd;border-radius:6px;padding:8px;font-family:monospace;font-size:12px;white-space:pre-wrap;word-break:break-word}}
pre{{background:#f6f5f2;border:1px solid #ddd;border-radius:6px;padding:9px;font-size:11px;white-space:pre-wrap;word-break:break-word}}
.art{{padding:6px 0;border-bottom:1px solid #eee}} .art p{{font-size:12px;color:#666;margin:2px 0 0}}
table.dt{{width:100%;border-collapse:collapse;margin:2px 0 4px;font-size:12px}}
table.dt th{{text-align:left;background:#f5f4f1;padding:5px 8px;border:1px solid #e2e0dc;font-size:10px;text-transform:uppercase;letter-spacing:.03em;color:#777}}
table.dt td{{padding:5px 8px;border:1px solid #eee}}
table.dt .num{{text-align:right;font-variant-numeric:tabular-nums}}
.foot{{margin-top:22px;padding-top:10px;border-top:1px solid #ddd;font-size:10px;color:#999;text-align:center}}
</style></head><body>
<div class="head">{logo_tag}<div><div class="t">SEO Audit Report</div><div class="sub">{e(ctx.get('url'))} · {e(ctx.get('kw'))} · {e(ctx.get('sector'))}</div></div></div>
{opt('Current state', a.get('current_state'))}
{opt('Diagnostic', a.get('diagnostic'))}
<div class="h">Optimized title tag</div><code>{e(a.get('title_tag'))}</code>
<div class="h">Meta description</div><code>{e(a.get('meta_description'))}</code>
<div class="h">Structured data (Schema.org)</div><pre>{e(schema)}</pre>
{vol_html}
{ranked_html}
<div class="h">Content plan</div>{arts}
{opt('Quick win', a.get('quick_win'))}
<div class="h">Next step — Book your Strategy Call</div>
<p>Your personalized audit is ready. Book a free 30-min strategy call to prioritize these fixes together:<br>
<a href="{CALENDLY_URL}" style="color:#DE9463;font-weight:700">Book your Strategy Call &rarr;</a></p>
<div class="foot">BuiltOnResults — SEO Audit · builtonresults.co.ke</div>
</body></html>'''

def render_pdf(html):
    chrome = find_chrome()
    if not chrome:
        print("⚠️  render_pdf: chrome not found"); return None
    try:
        with tempfile.TemporaryDirectory() as d:
            hp = os.path.join(d, 'a.html'); pp = os.path.join(d, 'a.pdf')
            with open(hp, 'w') as f:
                f.write(html)
            subprocess.run([chrome, '--headless', '--disable-gpu', '--no-sandbox',
                            '--no-pdf-header-footer', '--print-to-pdf=' + pp, 'file://' + hp],
                           timeout=45, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(pp):
                return open(pp, 'rb').read()
    except Exception as ex:
        print(f"⚠️  render_pdf error: {ex}")
    return None

def brevo_send(to_email, subject, html, attachment=None):
    """General Brevo transactional send. attachment = {'content': b64, 'name': ...} or None."""
    key, sender = _email_config()
    if not key or not sender:
        return False, 'not_configured'
    body = {"sender": {"name": "BuiltOnResults", "email": sender}, "to": [{"email": to_email}],
            "subject": subject, "htmlContent": html}
    if attachment:
        body["attachment"] = [attachment]
    try:
        req = urllib.request.Request("https://api.brevo.com/v3/smtp/email",
                                     data=json.dumps(body).encode(),
                                     headers={"api-key": key, "content-type": "application/json",
                                              "accept": "application/json"})
        urllib.request.urlopen(req, timeout=25).read()
        return True, None
    except Exception as ex:
        print(f"⚠️  brevo_send error: {ex}"); return False, 'send_failed'

def send_pdf_email(to_email, pdf_bytes):
    html = ("<p>Hi,</p><p>Your personalized SEO audit is attached as a PDF. Thanks for your order!</p>"
            "<p><strong>Next step:</strong> book your free 30-min strategy call to prioritize these "
            "fixes together:<br>"
            f'<a href="{CALENDLY_URL}" style="display:inline-block;margin-top:8px;background:#141210;'
            'color:#fff;padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:700">'
            'Book your Strategy Call &rarr;</a></p><p>&mdash; Elson, BuiltOnResults</p>')
    att = {"content": base64.b64encode(pdf_bytes).decode(), "name": "seo-audit.pdf"}
    return brevo_send(to_email, "Your SEO Audit — BuiltOnResults", html, att)

def build_free_plan_html(name, keyword, sector, scorecard=None, extra=None):
    """Free SEO preview email (lead nurture) — a nicely-formatted STRUCTURED REPORT that mirrors
    what the prospect saw on-screen: revenue potential + real on-page scorecard + top competitors
    + first fixes + CTA to the paid audit. Email-safe HTML (inline styles, table layout).
      scorecard = dict from scorecard_checks() or None
      extra = {url, market, revenue, currency, position, gain, competitors:[...]} or None"""
    e = lambda s: str(s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    x = extra or {}
    hi = f"Hi {e(name)}," if name else "Hi,"
    kw = e(keyword) or "your keyword"
    url = e(x.get('url'))
    market_lbl = {'global': 'Global', 'us': 'United States', 'eu': 'Europe',
                  'africa': 'Africa', 'asia': 'Asia'}.get(x.get('market'), '')
    C = '#171512'; CORAL = '#DE9463'; CREAM = '#F5F0E7'; LINE = '#e7e2d8'

    # ── Header ──
    subbits = ' &middot; '.join(b for b in [url, f'🔑 {kw}', e(sector).title(), market_lbl] if b)
    header = (
        f'<tr><td style="padding:22px 26px;border-bottom:2px solid {C}">'
        f'<div style="font-family:Georgia,serif;font-size:20px;font-weight:700;color:{C}">'
        'BuiltOnResults <span style="font-weight:400;color:#777;font-size:14px">— SEO Audit Preview</span></div>'
        f'<div style="font-size:12px;color:#777;margin-top:4px">{subbits}</div></td></tr>')

    # ── Revenue potential box ──
    rev_html = ''
    try:
        rev = int(x.get('revenue') or 0)
    except (TypeError, ValueError):
        rev = 0
    if rev > 0:
        cur = e(x.get('currency') or ''); pos = e(x.get('position') or '')
        gain = e(x.get('gain'))
        real = str(x.get('real')) in ('1', 'true', 'True')
        # Honesty: only claim a rank when we actually found the site on Google. Otherwise say so
        # plainly (it's also a stronger pitch — a clear, untapped opportunity).
        if real and pos:
            rank_line = (f'<div style="font-size:12px;color:#555;margin-top:6px">Currently ranking '
                         f'<strong>#{pos}</strong> on Google &middot; reaching the Top 3 could add '
                         f'<strong>+{gain}</strong> visitors/month</div>')
        else:
            rank_line = ('<div style="font-size:12px;color:#555;margin-top:6px">Your site is '
                         '<strong>not yet in Google\'s Top 10</strong> for this keyword — the steps '
                         'below are the first steps needed to get visible and rank in the Top 3.</div>')
        rev_html = (
            f'<tr><td style="padding:18px 26px 4px">'
            f'<div style="background:{CREAM};border:1px solid {LINE};border-radius:12px;padding:16px 18px">'
            '<div style="font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:#8a857d;font-weight:700">'
            'Estimated revenue potential</div>'
            f'<div style="font-size:26px;font-weight:800;color:{C};margin-top:2px">+{rev:,} {cur}'
            '<span style="font-size:13px;font-weight:400;color:#8a857d"> / month</span></div>'
            f'{rank_line}'
            '<div style="font-size:11px;color:#a8a29a;margin-top:8px">Estimate from sector averages '
            '(search volume, order value, conversion) — a full audit tunes it to your real numbers.</div>'
            '</div></td></tr>')

    # ── On-page scorecard ──
    sc_html = ''
    if scorecard and scorecard.get('checks'):
        passed, total = scorecard['passed'], scorecard['total']
        col = '#059669' if passed >= 7 else ('#d97706' if passed >= 4 else '#dc2626')
        rows = ''.join(
            f'<tr><td width="26" style="padding:6px 4px 6px 0;font-size:14px;vertical-align:top">'
            f'{"✅" if c["ok"] else "❌"}</td>'
            f'<td style="padding:6px 0;font-size:13px;color:#333;border-bottom:1px solid #f0ede6">'
            f'{e(c["k"])}</td></tr>'
            for c in scorecard['checks'])
        sc_html = (
            '<tr><td style="padding:18px 26px 4px">'
            '<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:8px"><tr>'
            f'<td style="font-size:14px;font-weight:700;color:{C}">🔎 On-page health '
            '<span style="font-weight:400;color:#8a857d;font-size:12px">— real facts from your live page</span></td>'
            f'<td align="right"><span style="font-weight:800;color:{col};border:2px solid {col};'
            f'border-radius:100px;padding:2px 10px;font-size:14px">{passed}/{total}</span></td></tr></table>'
            f'<table width="100%" cellpadding="0" cellspacing="0">{rows}</table>'
            '<div style="font-size:12px;color:#8a857d;margin-top:8px">Each ❌ is a concrete fix — the full audit '
            'gives you the exact ready-to-paste title, meta &amp; schema to resolve them.</div></td></tr>')

    # ── Competitors ──
    comp = [c for c in (x.get('competitors') or []) if c][:5]
    comp_html = ''
    if comp:
        chips = ''.join(
            f'<span style="display:inline-block;background:#fff;border:1px solid rgba(124,61,31,.3);'
            f'border-radius:100px;padding:3px 10px;font-size:12px;font-weight:600;color:#7c3d1f;'
            f'margin:0 6px 6px 0">#{i+1} {e(c)}</span>' for i, c in enumerate(comp))
        comp_html = (
            '<tr><td style="padding:18px 26px 4px">'
            f'<div style="font-size:14px;font-weight:700;color:{C};margin-bottom:8px">🏆 Who outranks you on Google '
            '<span style="font-weight:400;color:#8a857d;font-size:12px">(Top 10)</span></div>'
            f'{chips}'
            '<div style="font-size:12px;color:#8a857d;margin-top:2px">The full report breaks down what these '
            'pages do better — and your plan to overtake them.</div></td></tr>')

    # ── First fixes ──
    fixes = (
        '<tr><td style="padding:18px 26px 4px">'
        f'<div style="font-size:14px;font-weight:700;color:{C};margin-bottom:2px">📋 Your first steps to rank in the Top 3</div>'
        '<div style="font-size:12px;color:#8a857d;margin-bottom:6px">The first steps you need to get visible on Google for '
        f'"{kw}" and rank in the Top 3:</div>'
        f'<ol style="margin:0;padding-left:20px;color:#333;font-size:13px;line-height:1.7">'
        f'<li><strong>Put "{kw}" in your page title &amp; meta description</strong> — the first thing Google reads.</li>'
        '<li><strong>Add Schema.org structured data</strong> — helps Google and AI search understand your business.</li>'
        f'<li><strong>Publish one focused page around "{kw}"</strong> — fresh, relevant content moves you up.</li>'
        '</ol></td></tr>')

    # ── CTA + footer ──
    cta = (
        '<tr><td style="padding:20px 26px 6px">'
        f'<div style="background:{C};border-radius:14px;padding:18px 20px;text-align:center">'
        '<div style="color:#fff;font-size:14px;font-weight:600;margin-bottom:4px">Get the full personalized audit</div>'
        '<div style="color:#c9c4bd;font-size:12px;margin-bottom:12px">Exact optimized title &amp; meta, ready-to-paste '
        'schema, real long-tail keywords <em>with search volumes</em>, quick-win keywords, a content plan, a PDF report '
        '&amp; a 30-min strategy call.</div>'
        '<a href="https://builtonresults.co.ke/audit#pricing" style="display:inline-block;background:#fff;'
        f'color:{C};padding:11px 22px;border-radius:100px;text-decoration:none;font-weight:700;font-size:13px">'
        'Get your full $15 audit &rarr;</a></div></td></tr>')
    footer = (
        f'<tr><td style="padding:14px 26px 24px;color:#a8a29a;font-size:11px;text-align:center">'
        '&mdash; Elson, BuiltOnResults &middot; builtonresults.co.ke</td></tr>')

    return (
        f'<div style="background:{CREAM};padding:20px 0;font-family:Arial,Helvetica,sans-serif">'
        '<table align="center" width="600" cellpadding="0" cellspacing="0" '
        f'style="max-width:600px;width:100%;background:#fff;border:1px solid {LINE};border-radius:16px;'
        'overflow:hidden;margin:0 auto">'
        f'<tr><td style="padding:16px 26px 0;color:#333;font-size:14px">{hi}</td></tr>'
        f'{header}{rev_html}{sc_html}{comp_html}{fixes}{cta}{footer}'
        '</table></div>')

def _is_safe_url(url):
    """SSRF guard: only http(s), and no private/loopback/link-local/reserved IPs."""
    try:
        p = urlparse(url)
        if p.scheme not in ('http', 'https') or not p.hostname:
            return False
        for fam, _, _, _, sa in socket.getaddrinfo(p.hostname, None):
            ip = ipaddress.ip_address(sa[0])
            if (ip.is_private or ip.is_loopback or ip.is_link_local
                    or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
                return False
        return True
    except Exception:
        return False

class _Extract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ''; self.in_title = False
        self.meta_desc = ''
        self.h1 = []; self.h2 = []
        self._cur = None; self._buf = []
        self.jsonld = []; self._in_ld = False; self._ld = []
        self.text_parts = []; self._skip = 0
        self.viewport = False; self.img_total = 0; self.img_alt = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title':
            self.in_title = True
        elif tag == 'meta' and a.get('name', '').lower() == 'description' and a.get('content'):
            self.meta_desc = a['content']
        elif tag == 'meta' and a.get('name', '').lower() == 'viewport':
            self.viewport = True
        elif tag == 'img':
            self.img_total += 1
            if (a.get('alt') or '').strip():
                self.img_alt += 1
        elif tag in ('h1', 'h2'):
            self._cur = tag; self._buf = []
        elif tag in ('script', 'style', 'noscript'):
            self._skip += 1
            if tag == 'script' and a.get('type', '').lower() == 'application/ld+json':
                self._in_ld = True; self._ld = []
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag in ('h1', 'h2') and self._cur == tag:
            t = ' '.join(''.join(self._buf).split())
            if t: (self.h1 if tag == 'h1' else self.h2).append(t)
            self._cur = None
        elif tag in ('script', 'style', 'noscript'):
            self._skip = max(0, self._skip - 1)
            if tag == 'script' and self._in_ld:
                self.jsonld.append(''.join(self._ld)); self._in_ld = False
    def handle_data(self, data):
        if self.in_title: self.title += data
        if self._cur is not None: self._buf.append(data)
        if self._in_ld: self._ld.append(data)
        if self._skip == 0 and data.strip():
            self.text_parts.append(data.strip())

def crawl_page(url, keyword):
    """Fetch the client page server-side and extract real SEO facts (0 API cost)."""
    if not _is_safe_url(url):
        return {'crawled': False, 'reason': 'unsafe_or_unreachable'}
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; BuiltOnResultsBot/1.0; +https://builtonresults.com)'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read(600000).decode('utf-8', 'ignore')  # cap 600KB
    except Exception:
        return {'crawled': False, 'reason': 'fetch_failed'}
    p = _Extract()
    try:
        p.feed(html)
    except Exception:
        pass
    title = ' '.join(p.title.split())
    full_text = ' '.join(' '.join(p.text_parts).split())
    body = full_text[:2500]
    meta = p.meta_desc.strip()
    kw = keyword.lower()
    schema_types = []
    for blob in p.jsonld:
        schema_types += re.findall(r'"@type"\s*:\s*"([^"]+)"', blob)
    mph = re.search(r'(\+?\d[\d\s().-]{7,}\d)', body)
    return {
        'crawled': True,
        'title': title,
        'meta_description': meta,
        'h1': p.h1[:5],
        'h2': p.h2[:8],
        'schema_present': sorted(set(schema_types)),
        'keyword_in_title': kw in title.lower(),
        'keyword_in_body': kw in body.lower(),
        'phone_found': mph.group(1).strip() if mph else None,
        'body_excerpt': body,
        # ── extra facts for the free on-page scorecard ──
        'title_len': len(title),
        'meta_len': len(meta),
        'h1_count': len(p.h1),
        'word_count': len(full_text.split()),
        'https': url.lower().startswith('https://'),
        'viewport': p.viewport,
        'img_total': p.img_total,
        'img_alt': p.img_alt,
    }

def scorecard_checks(page):
    """On-page health checks from a crawled page dict. Shared by fn=peek (on-screen)
    and the free lead email so both show the SAME real diagnosis. Returns None if not crawled."""
    if not page.get('crawled'):
        return None
    imgs = page.get('img_total', 0)
    checks = [
        {'k': 'Title tag present', 'ok': bool(page.get('title'))},
        {'k': 'Keyword in title', 'ok': bool(page.get('keyword_in_title'))},
        {'k': 'Title length (30-65)', 'ok': 30 <= page.get('title_len', 0) <= 65},
        {'k': 'Meta description', 'ok': bool(page.get('meta_description')) and 50 <= page.get('meta_len', 0) <= 165},
        {'k': 'Single H1 heading', 'ok': page.get('h1_count', 0) == 1},
        {'k': 'Structured data (schema)', 'ok': bool(page.get('schema_present'))},
        {'k': 'Image alt coverage', 'ok': imgs == 0 or page.get('img_alt', 0) / max(1, imgs) >= 0.7},
        {'k': 'Mobile viewport', 'ok': bool(page.get('viewport'))},
        {'k': 'HTTPS', 'ok': bool(page.get('https'))},
        {'k': 'Content depth (300+ words)', 'ok': page.get('word_count', 0) >= 300},
    ]
    return {'checks': checks, 'passed': sum(1 for c in checks if c['ok']), 'total': len(checks)}

def llm_analyze(url, keyword, sector, market, position, aov, currency, lang, do_crawl=True, premium=False):
    """First-level SEO analysis via DeepSeek — relevant but deliberately not exhaustive.
    premium=True adds REAL DataForSEO data (search volumes + already-ranking quick wins)."""
    ck = (url.strip().lower(), keyword.strip().lower(), sector, lang, do_crawl, premium)
    now = time.time()
    c = analyze_cache.get(ck)
    if c and (now - c['ts']) < CACHE_TTL:
        r = dict(c['result']); r['cached'] = True; return r

    page = crawl_page(url, keyword) if do_crawl else {'crawled': False, 'reason': 'skipped'}

    # Paid audit: get the REAL deep ranking (Top-100) when the free tool couldn't place the site in
    # the Top-10 (position empty/0). The $15 deliverable is worth the ~$0.02 accurate lookup; if the
    # site genuinely doesn't rank, position stays empty and the prompt says so honestly.
    _p = str(position or '').strip().lstrip('#')
    if premium and (not _p or _p == '0'):
        try:
            sr = search_google(keyword, url, market, depth=100)
            position = sr.get('position') if sr.get('found') else ''
        except Exception as e:
            print(f"⚠️  deep rank lookup error: {e}")

    lang_name = 'French' if lang == 'fr' else 'English'
    sys_prompt = (
        "You are a senior SEO consultant producing a paid FIRST-LEVEL audit deliverable "
        "for a small business. Be concrete, specific and ready-to-use — the client paid for this. "
        "But keep it FIRST-LEVEL: give direction and ready-to-paste snippets, and leave full "
        "implementation, copywriting and technical setup as the paid next step (do not do everything). "
        "CRITICAL: NEVER invent contact details (phone, address, business name, hours, ratings) or "
        "any fact not present in the REAL PAGE DATA. When a value is unknown, use a clearly marked "
        "placeholder like [your phone] or [your address]. Base every recommendation on the REAL PAGE "
        "DATA when provided, and refer to what the page actually has today. "
        f"Write ALL human-readable text in {lang_name}. Output STRICT JSON only, matching the schema."
    )
    schema_hint = (
        '{"current_state":"1-2 sentences on what the page has TODAY (its title, whether schema exists, '
        'whether the keyword appears) — based ONLY on real data, or state data was unavailable",'
        '"diagnostic":"2-3 sentences: why this site likely ranks at this position for the keyword",'
        '"title_tag":"optimized <title>, <=60 chars, ready to paste",'
        '"meta_description":"ready to paste, <=155 chars",'
        '"schema_jsonld":{...schema.org JSON-LD for the sector; placeholders for any contact detail not in page data...},'
        '"long_tail_keywords":["5 to 6 long-tail variations grounded in the real services/content"],'
        '"content_plan":[{"title":"article title","why":"1 line: why it ranks / who it captures"}],'
        '"quick_win":"one concrete Google Business Profile / local action",'
        '"consultant_brief":{"priorities":["3-5 ranked actions to raise on the call, most impactful first"],'
        '"already_good":["what the site already does well — do NOT tell the client to redo these"],'
        '"upsell":["concrete paid follow-up services to offer this client"],'
        '"talking_points":["short phrases the consultant can say on the call"]}}'
    )
    if page.get('crawled'):
        pd = {k: page[k] for k in ('title', 'meta_description', 'h1', 'h2', 'schema_present',
                                   'keyword_in_title', 'keyword_in_body', 'phone_found', 'body_excerpt')}
        page_block = ("REAL PAGE DATA (crawled from the live site — use it, do not contradict it):\n"
                      + json.dumps(pd, ensure_ascii=False))
    else:
        page_block = (f"REAL PAGE DATA: unavailable ({page.get('reason')}). "
                      "Do NOT invent facts; use clearly marked placeholders for anything unknown.")
    # Honesty: only state a rank when it's a REAL Google position. The free tool sends an empty
    # position when the site isn't in the Top 10, so we must NOT feed the LLM a fabricated rank.
    pos_str = str(position or '').strip().lstrip('#')
    if pos_str and pos_str != '0':
        rank_line = f"Current Google position: #{pos_str}"
    else:
        rank_line = ("Current Google ranking: NOT ranking in the Top 10 for this keyword "
                     "(treat the page as unranked / new for this term — do NOT claim a specific position)")
    user_prompt = (
        f"Business site: {url}\nTarget keyword: {keyword}\nSector: {sector}\nMarket: {market}\n"
        f"{rank_line}\nAverage order value: {aov} {currency}\n\n"
        f"{page_block}\n\n"
        f"Produce the deliverable as JSON with EXACTLY these keys: {schema_hint}\n"
        "content_plan must have exactly 3 items. long_tail_keywords 5-6 items. "
        "The 'consultant_brief' is PRIVATE notes for the consultant (never shown to the client) "
        "— be candid about priorities, what to skip, and what to upsell."
    )
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": sys_prompt},
                     {"role": "user", "content": user_prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.4,
        "max_tokens": 1600,
    }).encode()
    req = urllib.request.Request(DEEPSEEK_URL, data=payload)
    req.add_header('Authorization', f'Bearer {DEEPSEEK_KEY}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read())
    parsed = json.loads(data['choices'][0]['message']['content'])
    usage = data.get('usage', {})
    # ── Premium enrichment: attach REAL search data (paid path only) ──
    # Runs AFTER the LLM so we can price the LLM's own long-tail suggestions with real volumes.
    if premium:
        try:
            lt = parsed.get('long_tail_keywords') or []
            vols = dataforseo_volumes([keyword] + [k for k in lt if isinstance(k, str)], market)
            if vols:
                parsed['keyword_volumes'] = vols
            ranked = dataforseo_ranked(url, market)
            if ranked:
                parsed['ranked_keywords'] = ranked
            parsed['premium_data'] = bool(vols or ranked)
        except Exception as e:
            print(f"⚠️  premium enrichment error: {e}")
    result = {'ok': True, 'analysis': parsed, 'source': 'deepseek',
              'crawled': page.get('crawled', False), 'premium': premium,
              'tokens': usage.get('total_tokens', 0)}
    analyze_cache[ck] = {'result': result, 'ts': now}
    if len(analyze_cache) > 300:
        for k in [k for k, v in analyze_cache.items() if now - v['ts'] >= CACHE_TTL]:
            del analyze_cache[k]
    return result

def search_google(query, site_url, market='global', depth=10):
    """Search real Google position for a site on a keyword (cached 1h).
    depth=10 (free tool, ~$0.002, Google page 1) · depth=100 (paid audit, ~$0.02, real deep rank)."""
    cache_key = (query.strip().lower(), site_url.strip().lower(), market, depth)
    now = time.time()
    cached = search_cache.get(cache_key)
    if cached and (now - cached['ts']) < CACHE_TTL:
        r = dict(cached['result']); r['cached'] = True; return r

    # 2840=US, 2826=UK, 2404=Kenya. FIX: africa was 2840 (US) — wrong; set to Kenya (target market).
    # NOTE: 'asia' (2860) kept as-is but broad-zone codes should be reviewed with OG-Elson.
    loc = LOCATION_CODES.get(market, 0)

    # depth 10 (Google page 1): keeps the free-tier call cheap (~$0.002 vs ~$0.02 at depth 100).
    # The paid audit passes depth=100 to report the REAL deep ranking. If not found, we say so
    # HONESTLY rather than inventing a position.
    payload = json.dumps([{"keyword": query, "location_code": loc, "language_code": "en", "depth": depth}]).encode()
    req = urllib.request.Request(API_URL, data=payload)
    req.add_header('Authorization', f'Basic {AUTH_BASE64}')
    req.add_header('Content-Type', 'application/json')

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    log_usage('serp', data.get('cost', 0), f"{query} | depth={depth} | {market}")

    domain = urlparse(site_url).netloc if '://' in site_url else site_url
    domain = re.sub(r'^www\.', '', domain).lower()

    items = []
    if data.get('tasks') and data['tasks'][0].get('result'):
        items = data['tasks'][0]['result'][0].get('items', [])

    positions = []
    first_url = None
    competitors = []
    for i, item in enumerate(items):
        d = (item.get('domain') or '').lower()
        u = (item.get('url') or item.get('link') or '')
        if domain in d or domain in u:
            positions.append(i + 1)
            if not first_url: first_url = u
        else:
            cd = re.sub(r'^www\.', '', d)
            if cd and cd not in competitors:
                competitors.append(cd)
    competitors = competitors[:5]

    if positions:
        result = {'position': min(positions), 'found': True, 'count': len(positions), 'url': first_url, 'competitors': competitors, 'source': 'Google (DataForSEO)', 'cost': data.get('cost', 0)}
    else:
        result = {'position': None, 'found': False, 'url': None, 'competitors': competitors, 'source': 'Google (DataForSEO)', 'cost': data.get('cost', 0)}

    # Store + purge expired entries (bounded memory, like request_log)
    search_cache[cache_key] = {'result': result, 'ts': now}
    if len(search_cache) > 500:
        for k in [k for k, v in search_cache.items() if now - v['ts'] >= CACHE_TTL]:
            del search_cache[k]
    return result

def _dfs_post(url, payload_list, timeout=30):
    """POST helper for DataForSEO live endpoints. Returns tasks[0].result or None."""
    if not AUTH_BASE64:
        return None
    req = urllib.request.Request(url, data=json.dumps(payload_list).encode())
    req.add_header('Authorization', f'Basic {AUTH_BASE64}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    ep = 'volumes' if 'search_volume' in url else ('ranked' if 'ranked_keywords' in url else 'dfs')
    log_usage(ep, data.get('cost', 0), url.rsplit('/v3/', 1)[-1])
    tasks = data.get('tasks') or []
    if not tasks or tasks[0].get('status_code') != 20000:
        return None
    return {'result': tasks[0].get('result') or [], 'cost': data.get('cost', 0)}

def dataforseo_volumes(keywords, market='global'):
    """Real Google search volumes for a list of keywords (PAID path only, ~$0.05/call).
    Returns [{'keyword','volume','cpc','competition'}] sorted by volume desc, or []."""
    kws = [k.strip() for k in keywords if k and k.strip()][:20]
    if not kws:
        return []
    loc = LOCATION_CODES.get(market, 2840)
    try:
        r = _dfs_post(DFS_VOLUME_URL, [{"keywords": kws, "location_code": loc,
                                        "language_code": "en"}])
    except Exception as e:
        print(f"⚠️  dataforseo_volumes error: {e}"); return []
    if not r:
        return []
    out = []
    for item in r['result']:
        kw = item.get('keyword')
        if not kw:
            continue
        out.append({
            'keyword': kw,
            'volume': item.get('search_volume') or 0,
            'cpc': round(item.get('cpc') or 0, 2),
            'competition': (item.get('competition') or '').lower() or None,
        })
    out.sort(key=lambda x: x['volume'] or 0, reverse=True)
    return out

def dataforseo_ranked(site_url, market='global', limit=10):
    """Keywords the site ALREADY ranks for (quick wins), via DataForSEO Labs (~$0.02/call).
    Returns [{'keyword','position','volume'}] for positions 4-30, sorted by volume desc, or []."""
    domain = urlparse(site_url).netloc if '://' in site_url else site_url
    domain = re.sub(r'^www\.', '', domain).lower().strip('/')
    if not domain:
        return []
    loc = LOCATION_CODES.get(market, 2840)
    try:
        # Server-side filter: "quick wins" = already ranking pos 4-30 (page 1-3, not top-3),
        # ordered by real search volume desc. Without the filter the API returns the site's
        # #1 rankings first, drowning out the actionable opportunities.
        r = _dfs_post(DFS_RANKED_URL, [{"target": domain, "location_code": loc,
                                        "language_code": "en", "limit": limit,
                                        "filters": [["ranked_serp_element.serp_item.rank_group", ">=", 4],
                                                    "and",
                                                    ["ranked_serp_element.serp_item.rank_group", "<=", 30]],
                                        "order_by": ["keyword_data.keyword_info.search_volume,desc"]}])
    except Exception as e:
        print(f"⚠️  dataforseo_ranked error: {e}"); return []
    if not r or not r['result']:
        return []
    items = (r['result'][0] or {}).get('items') or []
    out = []
    for it in items:
        kd = it.get('keyword_data') or {}
        kw = kd.get('keyword')
        vol = ((kd.get('keyword_info') or {}).get('search_volume')) or 0
        serp = ((it.get('ranked_serp_element') or {}).get('serp_item') or {})
        pos = serp.get('rank_group') or serp.get('rank_absolute')
        if not kw or not pos:
            continue
        out.append({'keyword': kw, 'position': pos, 'volume': vol})
    return out[:limit]

def do_approve_payment(params):
    """Validate the magic link + generate & send the client PDF. Returns a rich dict."""
    pid = params.get('id', [''])[0]; token = params.get('token', [''])[0]
    r = _find_jsonl(PENDING_PAYMENTS, 'id', pid)
    if not r or not token or not secrets.compare_digest(token, r.get('token', '')):
        return {'ok': False, 'reason': 'invalid'}
    info = {'client_email': r.get('email', ''), 'method': r.get('method', ''), 'txn': r.get('txn', ''),
            'ts_eat': (datetime.now(timezone.utc) + timedelta(hours=3)).strftime('%d/%m/%Y %H:%M')}
    if r.get('status') == 'sent':
        return {'ok': False, 'reason': 'already_sent', **info}
    if int(time.time()) - int(r.get('epoch', 0)) > 86400:
        return {'ok': False, 'reason': 'expired', **info}
    try:
        res = llm_analyze(r.get('url', ''), r.get('keyword', ''), r.get('sector', ''),
                          r.get('market', 'global'), r.get('position', '0'), r.get('aov', '0'),
                          r.get('currency', ''), r.get('lang', 'en'), premium=True)
        if not res.get('ok'):
            return {'ok': False, 'reason': 'error', **info}
        html = build_audit_html(res['analysis'], {'url': r.get('url'), 'kw': r.get('keyword'),
                                                  'sector': r.get('sector')})
        pdf = render_pdf(html)
        if not pdf:
            return {'ok': False, 'reason': 'pdf_failed', **info}
        ok, reason = send_pdf_email(r['email'], pdf)
        if not ok:
            return {'ok': False, 'reason': reason or 'send_failed', **info}
        _update_jsonl(PENDING_PAYMENTS, 'id', pid, {'status': 'sent'})
        umami_track('paid_success', {'method': r.get('method', '')})
        return {'ok': True, 'message': f"Report sent to {r['email']}", **info}
    except Exception as e:
        print(f"⚠️  approve_payment: {e}")
        return {'ok': False, 'reason': 'error', **info}

def approval_page_html(res):
    """Branded HTML page for the payment-approval magic link (BuiltOnResults look)."""
    esc = lambda s: str(s if s is not None else '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    ok = res.get('ok')
    reasons = {
        'invalid': 'This approval link is invalid. Make sure you used the exact link from the email.',
        'expired': 'This approval link has expired (valid 24h). Ask the client to submit the payment claim again.',
        'already_sent': 'This report was already approved and sent — nothing more to do.',
        'pdf_failed': 'The PDF could not be generated. Try clicking the link again in a moment.',
        'send_failed': 'The email could not be sent — check the Brevo configuration.',
        'not_configured': 'Email delivery is not configured (Brevo key missing).',
        'error': 'Something went wrong generating the report. Try again.',
    }
    title = '&#9989; Approval confirmed' if ok else '&#9888;&#65039; Approval failed'
    def det(rows):
        return ('<div class="det">' + ''.join(f'<div><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in rows if v) + '</div>')
    if ok:
        lead = f'PDF report sent to <strong>{esc(res.get("client_email"))}</strong> via Brevo.'
        block = det([('Payment method', (res.get('method') or '').upper()),
                     ('Transaction ID', res.get('txn')), ('Timestamp', (res.get('ts_eat', '') + ' EAT') if res.get('ts_eat') else '')])
    else:
        lead = esc(reasons.get(res.get('reason'), 'Unknown error.'))
        block = det([('Client', res.get('client_email')), ('Method', (res.get('method') or '').upper()),
                     ('Transaction', res.get('txn'))]) if res.get('client_email') else ''
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{'Approval confirmed' if ok else 'Approval failed'} — BuiltOnResults</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Arial,Helvetica,sans-serif;background:#F5F0E7;color:#141210;line-height:1.6;padding:1.5rem;min-height:100vh;display:flex;align-items:center;justify-content:center}}
.card{{background:#FBF8F2;border:1px solid rgba(20,18,16,.12);border-radius:18px;padding:2rem 1.6rem;max-width:600px;width:100%;text-align:center;box-shadow:0 12px 40px rgba(20,18,16,.07)}}
.logo{{height:44px;width:auto;margin:0 auto .6rem;display:block}}
.bar{{height:4px;width:56px;background:#E8A87C;border-radius:4px;margin:0 auto 1.3rem}}
h1{{font-family:Georgia,'Times New Roman',serif;font-size:1.6rem;margin-bottom:1rem}}
.lead{{font-size:1.02rem;color:#3a3630;margin-bottom:.6rem}}
.det{{text-align:left;background:#F5F0E7;border:1px solid rgba(20,18,16,.1);border-radius:12px;padding:.4rem 1.1rem;margin:1.3rem 0}}
.det div{{display:flex;justify-content:space-between;gap:1rem;padding:.5rem 0;font-size:.94rem;border-bottom:1px solid rgba(20,18,16,.08)}}
.det div:last-child{{border-bottom:none}}
.det span{{color:#6f6a63}}
.det b{{color:#141210;word-break:break-word;text-align:right}}
.btn{{display:inline-block;margin-top:.6rem;background:#141210;color:#fff;padding:.75rem 1.7rem;border-radius:100px;text-decoration:none;font-weight:600;font-size:.95rem}}
@media(max-width:480px){{body{{padding:1rem;font-size:16px}}.card{{padding:1.6rem 1.1rem}}h1{{font-size:1.4rem}}}}
</style></head><body>
<div class="card">
<img class="logo" src="https://builtonresults.co.ke/logo-br.png" alt="BuiltOnResults">
<div class="bar"></div>
<h1>{title}</h1>
<p class="lead">{lead}</p>
{block}
<a class="btn" href="https://builtonresults.co.ke">Return to site</a>
</div></body></html>'''

def do_qualify_brief(params):
    """Magic-link action on a project brief: qualify (send Calendly) or decline (polite + audit upsell)."""
    bid = params.get('id', [''])[0]; token = params.get('token', [''])[0]; action = params.get('action', [''])[0]
    r = _find_jsonl(PENDING_BRIEFS, 'id', bid)
    if not r or action not in ('qualify', 'decline') or not token or not hmac.compare_digest(token, brief_token(bid)):
        return {'ok': False, 'reason': 'invalid'}
    info = {'name': r.get('name', ''), 'email': r.get('email', ''), 'project_type': r.get('project_type', '')}
    if r.get('status') != 'new':
        return {'ok': False, 'reason': 'already_done', 'status': r.get('status'), **info}
    if int(time.time()) - int(r.get('epoch', 0)) > 7 * 86400:
        return {'ok': False, 'reason': 'expired', **info}
    name = r.get('name', '') or 'there'
    if action == 'qualify':
        subject = "Let's talk about your project"
        html = (f"<p>Hi {name},</p><p>Thanks for sharing your brief on {r.get('project_type', 'your project')}. "
                "Based on what you shared, I'd love to discuss it further.</p>"
                f'<p>Book a 20-min discovery call here:<br><a href="{DISCOVERY_CAL}">{DISCOVERY_CAL}</a></p>'
                "<p>Looking forward to talking soon,<br>Elson &mdash; BuiltOnResults</p>")
        new_status = 'qualified'
    else:
        subject = "Thanks for reaching out"
        html = (f"<p>Hi {name},</p><p>Thanks for your interest in working with me. Based on your brief, "
                "my current focus doesn't fully align with what you're looking for right now.</p>"
                f'<p>In the meantime, our $15 SEO Audit might be a great fit to get started:<br>'
                f'<a href="{GUMROAD_URL}">{GUMROAD_URL}</a></p>'
                "<p>All the best,<br>Elson &mdash; BuiltOnResults</p>")
        new_status = 'declined'
    try:
        brevo_send(r['email'], subject, html)
    except Exception as e:
        print(f"⚠️  qualify_brief email: {e}")
    _update_jsonl(PENDING_BRIEFS, 'id', bid, {'status': new_status})
    umami_track('brief_' + new_status)  # brief_qualified | brief_declined
    return {'ok': True, 'action': action, 'status': new_status, **info}

def brief_page_html(res):
    esc = lambda s: str(s if s is not None else '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    ok = res.get('ok')
    if ok and res.get('action') == 'qualify':
        title = '&#9989; Brief qualified'
        lead = f'Discovery-call invite sent to <strong>{esc(res.get("email"))}</strong>.'
    elif ok:
        title = '&#128078; Brief declined'
        lead = f'A polite decline (with the $15 audit) was sent to <strong>{esc(res.get("email"))}</strong>.'
    else:
        reasons = {'invalid': 'This link is invalid.', 'expired': 'This link has expired (valid 7 days).',
                   'already_done': f'This brief was already handled (status: {esc(res.get("status"))}).'}
        title = '&#9888;&#65039; Action failed'
        lead = esc(reasons.get(res.get('reason'), 'Unknown error.'))
    rows = ''
    if res.get('name') or res.get('email'):
        rows = (f'<div class="det"><div><span>Client</span><b>{esc(res.get("name"))}</b></div>'
                f'<div><span>Email</span><b>{esc(res.get("email"))}</b></div>'
                f'<div><span>Project</span><b>{esc(res.get("project_type"))}</b></div></div>')
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>Brief — BuiltOnResults</title><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Arial,Helvetica,sans-serif;background:#F5F0E7;color:#141210;line-height:1.6;padding:1.5rem;min-height:100vh;display:flex;align-items:center;justify-content:center}}
.card{{background:#FBF8F2;border:1px solid rgba(20,18,16,.12);border-radius:18px;padding:2rem 1.6rem;max-width:600px;width:100%;text-align:center;box-shadow:0 12px 40px rgba(20,18,16,.07)}}
.logo{{height:44px;width:auto;margin:0 auto .6rem;display:block}}.bar{{height:4px;width:56px;background:#E8A87C;border-radius:4px;margin:0 auto 1.3rem}}
h1{{font-family:Georgia,'Times New Roman',serif;font-size:1.6rem;margin-bottom:1rem}}.lead{{font-size:1.02rem;color:#3a3630;margin-bottom:.6rem}}
.det{{text-align:left;background:#F5F0E7;border:1px solid rgba(20,18,16,.1);border-radius:12px;padding:.4rem 1.1rem;margin:1.3rem 0}}
.det div{{display:flex;justify-content:space-between;gap:1rem;padding:.5rem 0;font-size:.94rem;border-bottom:1px solid rgba(20,18,16,.08)}}
.det div:last-child{{border-bottom:none}}.det span{{color:#6f6a63}}.det b{{color:#141210;word-break:break-word;text-align:right}}
.btn{{display:inline-block;margin-top:.6rem;background:#141210;color:#fff;padding:.75rem 1.7rem;border-radius:100px;text-decoration:none;font-weight:600;font-size:.95rem}}
@media(max-width:480px){{body{{padding:1rem;font-size:16px}}.card{{padding:1.6rem 1.1rem}}h1{{font-size:1.4rem}}}}
</style></head><body><div class="card">
<img class="logo" src="https://builtonresults.co.ke/logo-br.png" alt="BuiltOnResults"><div class="bar"></div>
<h1>{title}</h1><p class="lead">{lead}</p>{rows}
<a class="btn" href="https://builtonresults.co.ke">Return to site</a></div></body></html>'''

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, ctype, body):
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Rate limiting (trust X-Forwarded-For when behind the nginx reverse proxy)
        client_ip = self.headers.get('X-Forwarded-For', self.client_address[0]).split(',')[0].strip()
        now = time.time()
        # Purge expired entries and clean up empty IP keys
        to_purge = []
        for ip in list(request_log.keys()):
            request_log[ip] = [t for t in request_log[ip] if now - t < RATE_WINDOW]
            if not request_log[ip]:
                to_purge.append(ip)
        for ip in to_purge:
            del request_log[ip]
        
        if len(request_log.get(client_ip, [])) >= RATE_LIMIT:
            self.send_response(429)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Retry-After', str(RATE_WINDOW))
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Too many requests. Try again in 60s.', 'limit': RATE_LIMIT}).encode())
            return
        request_log[client_ip].append(now)
        
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        # approve_payment renders a branded HTML page (clicked by OG-Elson in a browser).
        # JSON stays available via `Accept: application/json` for programmatic use.
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'approve_payment':
            res = do_approve_payment(params)
            if 'application/json' in (self.headers.get('Accept') or ''):
                self._send(200, 'application/json', json.dumps(res).encode())
            else:
                self._send(200, 'text/html; charset=utf-8', approval_page_html(res).encode('utf-8'))
            return
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'qualify_brief':
            res = do_qualify_brief(params)
            if 'application/json' in (self.headers.get('Accept') or ''):
                self._send(200, 'application/json', json.dumps(res).encode())
            else:
                self._send(200, 'text/html; charset=utf-8', brief_page_html(res).encode('utf-8'))
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'admin':
            # Consultant dashboard — gated by a SEPARATE admin code
            admins = get_admin_codes()
            if not admins or params.get('code', [''])[0].strip() not in admins:
                self.wfile.write(json.dumps({'ok': False, 'reason': 'invalid_code'}).encode()); return
            self.wfile.write(json.dumps({'ok': True, 'audits': read_audits(), 'leads': read_leads(),
                'briefs': [dict(b, token=brief_token(b.get('id', ''))) for b in read_briefs()]},
                ensure_ascii=False).encode()); return
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'mpesa_status':
            self.wfile.write(json.dumps(mpesa_status()).encode()); return
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'mpesa_reveal':
            # Reveal the M-Pesa number ONLY if the channel is open (server clock) + capture lead
            email = params.get('email', [''])[0].strip()
            name = params.get('name', [''])[0].strip()
            if not name or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
                self.wfile.write(json.dumps({'ok': False, 'reason': 'bad_form'}).encode()); return
            if not mpesa_status()['open']:
                self.wfile.write(json.dumps({'ok': False, 'reason': 'closed'}).encode()); return
            rec = {'ts': time.strftime('%Y-%m-%d %H:%M'), 'email': email[:160], 'name': name[:120],
                   'url': params.get('url', [''])[0], 'keyword': params.get('kw', [''])[0],
                   'sector': params.get('sector', [''])[0], 'position': params.get('pos', [''])[0], 'src': 'mpesa'}
            store_lead(rec); forward_lead(rec)
            self.wfile.write(json.dumps({'ok': True, 'number': get_mpesa_number(), 'amount': 'KES 2,000'}).encode()); return
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'peek':
            # FREE crawl teaser (no LLM, no code) — proves the paid audit looks at the real site
            try:
                pg = crawl_page(params.get('url', [''])[0], params.get('kw', [''])[0])
            except Exception as e:
                print(f"⚠️  peek error: {e}"); pg = {'crawled': False, 'reason': 'error'}
            sc = scorecard_checks(pg)
            if sc:
                out = {'ok': True, 'crawled': True, 'title': pg['title'][:160],
                       'keyword_in_title': bool(pg['keyword_in_title']), 'checks': sc['checks'],
                       'passed': sc['passed'], 'total': sc['total']}
            else:
                out = {'ok': True, 'crawled': False, 'reason': pg.get('reason')}
            self.wfile.write(json.dumps(out, ensure_ascii=False).encode()); return
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'lead':
            # Capture a non-buyer's email → store + forward to email automation
            email = params.get('email', [''])[0].strip()
            if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
                self.wfile.write(json.dumps({'ok': False, 'reason': 'bad_email'}).encode()); return
            kw = params.get('kw', [''])[0]
            # Idempotency: same email + keyword already got the free plan → no duplicate send.
            if _lead_already_emailed(email, kw):
                self.wfile.write(json.dumps({'ok': True, 'dedup': True, 'emailed': False}).encode()); return
            rec = {'ts': time.strftime('%Y-%m-%d %H:%M'), 'email': email[:160],
                   'name': params.get('name', [''])[0][:120], 'url': params.get('url', [''])[0],
                   'keyword': kw, 'sector': params.get('sector', [''])[0],
                   'position': params.get('pos', [''])[0], 'src': params.get('src', [''])[0][:20]}
            # Crawl the page ($0) to include the SAME real on-page scorecard the user saw on-screen.
            sc = None
            try:
                if rec['url']:
                    sc = scorecard_checks(crawl_page(rec['url'], kw))
            except Exception as e:
                print(f"⚠️  free plan crawl error: {e}")
            # Rebuild the on-screen preview context (revenue box + competitors) from what the
            # front-end already computed — no extra paid call.
            comp = [c.strip() for c in params.get('comp', [''])[0].split(',') if c.strip()][:5]
            extra = {'url': rec['url'], 'market': params.get('m', [''])[0],
                     'revenue': params.get('rev', [''])[0], 'currency': params.get('cur', [''])[0],
                     'position': rec['position'], 'gain': params.get('gain', [''])[0],
                     'competitors': comp}
            # send the structured free preview report by email (best-effort), then store the flag
            sent = False
            try:
                ok, _ = brevo_send(email, "Your free SEO audit preview — BuiltOnResults",
                                   build_free_plan_html(rec['name'], rec['keyword'], rec['sector'], sc, extra))
                sent = bool(ok)
            except Exception as e:
                print(f"⚠️  free plan email error: {e}")
            rec['emailed'] = sent
            store_lead(rec); forward_lead(rec)
            self.wfile.write(json.dumps({'ok': True, 'emailed': sent}).encode()); return
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'brief':
            # honeypot: hidden 'company' field — bots fill it → silently accept (don't tip them off)
            if params.get('company', [''])[0].strip():
                self.wfile.write(json.dumps({'ok': True}).encode()); return
            name = params.get('name', [''])[0].strip()
            email = params.get('email', [''])[0].strip()
            desc = params.get('description', [''])[0].strip()
            if not name or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email) or len(desc) < 20:
                self.wfile.write(json.dumps({'ok': False, 'reason': 'bad_form'}).encode()); return
            if _recent_brief(email):  # idempotency: same email in the last 10 min
                self.wfile.write(json.dumps({'ok': True, 'dedup': True}).encode()); return
            bid = 'brief_' + uuid.uuid4().hex[:12]
            rec = {'id': bid, 'ts': time.strftime('%Y-%m-%d %H:%M'), 'epoch': int(time.time()),
                   'name': name[:120], 'email': email[:160],
                   'project_type': params.get('project_type', [''])[0][:40],
                   'budget': params.get('budget', [''])[0][:40],
                   'timeline': params.get('timeline', [''])[0][:40],
                   'description': desc[:1500], 'status': 'new'}
            _append_jsonl(PENDING_BRIEFS, rec)
            umami_track('brief_received', {'project_type': rec.get('project_type', '')})
            token = brief_token(bid)
            qurl = f"{SITE}/api/search?fn=qualify_brief&id={bid}&token={token}&action=qualify"
            durl = f"{SITE}/api/search?fn=qualify_brief&id={bid}&token={token}&action=decline"
            e = lambda s: str(s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            admin_html = ("<p><strong>New project brief</strong></p><ul>"
                          f"<li>Name: {e(rec['name'])}</li><li>Email: {e(rec['email'])}</li>"
                          f"<li>Project: {e(rec['project_type'])}</li><li>Budget: {e(rec['budget'])}</li>"
                          f"<li>Timeline: {e(rec['timeline'])}</li></ul>"
                          f"<p><em>{e(rec['description'])}</em></p><p style=\"margin-top:16px\">"
                          f'<a href="{qurl}" style="background:#16a34a;color:#fff;padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:700;margin-right:8px">&#10003; Qualify</a>'
                          f'<a href="{durl}" style="background:#6b7280;color:#fff;padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:700">&#10007; Decline</a></p>')
            try:
                brevo_send(ADMIN_NOTIFY, "New project brief — qualify or decline", admin_html)
            except Exception as ex:
                print(f"⚠️  brief notify: {ex}")
            self.wfile.write(json.dumps({'ok': True}).encode()); return
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'pending_audit':
            aid = uuid.uuid4().hex[:16]
            _append_jsonl(PENDING_AUDITS, {
                'audit_id': aid, 'ts': time.strftime('%Y-%m-%d %H:%M'),
                'url': params.get('url', [''])[0], 'keyword': params.get('kw', [''])[0],
                'sector': params.get('sector', [''])[0], 'market': params.get('m', ['global'])[0],
                'email': params.get('email', [''])[0][:160], 'name': params.get('name', [''])[0][:120],
                'method_intent': params.get('method', [''])[0][:20]})
            self.wfile.write(json.dumps({'ok': True, 'audit_id': aid}).encode()); return
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'get_pending':
            r = _find_jsonl(PENDING_AUDITS, 'audit_id', params.get('audit_id', [''])[0])
            if not r:
                self.wfile.write(json.dumps({'ok': False}).encode()); return
            self.wfile.write(json.dumps({'ok': True, 'url': r.get('url'), 'keyword': r.get('keyword'),
                'sector': r.get('sector'), 'market': r.get('market'), 'email': r.get('email')}).encode()); return
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'pending_payment':
            email = params.get('email', [''])[0].strip()
            method = params.get('method', [''])[0].strip().lower()
            txn = params.get('txn', [''])[0].strip()
            if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email) or method not in ('paypal', 'mpesa') or not txn:
                self.wfile.write(json.dumps({'ok': False, 'reason': 'bad_form'}).encode()); return
            # Idempotency: one transaction ID = one claim. Re-submit / double-click → no duplicate,
            # no duplicate admin email. (Daemon is single-threaded, so this check is race-free.)
            if _find_jsonl(PENDING_PAYMENTS, 'txn', txn):
                self.wfile.write(json.dumps({'ok': True, 'dedup': True}).encode()); return
            pid = uuid.uuid4().hex[:16]; token = secrets.token_urlsafe(24)
            _append_jsonl(PENDING_PAYMENTS, {
                'id': pid, 'ts': time.strftime('%Y-%m-%d %H:%M'), 'epoch': int(time.time()),
                'email': email[:160], 'method': method, 'txn': txn[:80], 'status': 'pending', 'token': token,
                'url': params.get('url', [''])[0], 'keyword': params.get('kw', [''])[0],
                'sector': params.get('sector', [''])[0], 'market': params.get('m', ['global'])[0],
                'position': params.get('pos', ['0'])[0], 'aov': params.get('aov', ['0'])[0],
                'currency': params.get('cur', [''])[0], 'lang': params.get('lang', ['en'])[0],
                'name': params.get('name', [''])[0][:120]})
            link = f"{SITE}/api/search?fn=approve_payment&id={pid}&token={token}"
            admin_html = ("<p><strong>New payment claim</strong></p><ul>"
                          f"<li>Email: {email}</li><li>Method: {method}</li><li>Txn/Ref: {txn}</li>"
                          f"<li>Site: {params.get('url',[''])[0]} — keyword: {params.get('kw',[''])[0]}</li></ul>"
                          "<p>Verify the funds arrived, then click to generate &amp; send the report:</p>"
                          f'<p><a href="{link}" style="background:#141210;color:#fff;padding:10px 18px;'
                          'border-radius:8px;text-decoration:none;font-weight:700">✅ Approve &amp; send report</a></p>')
            try:
                brevo_send(ADMIN_NOTIFY, "💰 Payment claim — approve to send audit", admin_html)
            except Exception as e:
                print(f"⚠️  pending_payment notify: {e}")
            self.wfile.write(json.dumps({'ok': True}).encode()); return
        # (approve_payment handled earlier — returns branded HTML)
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'emailpdf':
            # Fallback delivery: generate the audit PDF server-side and email it (Brevo)
            codes = get_unlock_codes(); given = params.get('code', [''])[0].strip()
            email = params.get('email', [''])[0].strip()
            if not codes or given not in codes:
                self.wfile.write(json.dumps({'ok': False, 'reason': 'invalid_code'}).encode()); return
            if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
                self.wfile.write(json.dumps({'ok': False, 'reason': 'bad_email'}).encode()); return
            try:
                res = llm_analyze(  # cached from the unlock → no new LLM cost
                    params.get('url', [''])[0], params.get('kw', [''])[0],
                    params.get('sector', [''])[0], params.get('m', ['global'])[0],
                    params.get('pos', ['0'])[0], params.get('aov', ['0'])[0],
                    params.get('cur', [''])[0], params.get('lang', ['en'])[0],
                    do_crawl=(params.get('crawl', ['1'])[0] != '0'), premium=True)
                if not res.get('ok'):
                    self.wfile.write(json.dumps({'ok': False, 'reason': 'analyze_failed'}).encode()); return
                html = build_audit_html(res['analysis'], {'url': params.get('url', [''])[0],
                                        'kw': params.get('kw', [''])[0], 'sector': params.get('sector', [''])[0]})
                pdf = render_pdf(html)
                if not pdf:
                    self.wfile.write(json.dumps({'ok': False, 'reason': 'pdf_failed'}).encode()); return
                ok, reason = send_pdf_email(email, pdf)
                self.wfile.write(json.dumps({'ok': ok, 'reason': reason}).encode()); return
            except Exception as ex:
                print(f"⚠️  emailpdf error: {ex}")
                self.wfile.write(json.dumps({'ok': False, 'reason': 'error'}).encode()); return
        if parsed.path == '/search' and params.get('fn', [''])[0] == 'analyze':
            # Paid LLM deliverable — gated by unlock code (200 already sent → signal via JSON)
            codes = get_unlock_codes()
            given = params.get('code', [''])[0].strip()
            if not codes:
                self.wfile.write(json.dumps({'ok': False, 'reason': 'not_configured'}).encode()); return
            if given not in codes:
                self.wfile.write(json.dumps({'ok': False, 'reason': 'invalid_code'}).encode()); return
            if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', params.get('email', [''])[0].strip()):
                self.wfile.write(json.dumps({'ok': False, 'reason': 'bad_email'}).encode()); return
            if not DEEPSEEK_KEY:
                self.wfile.write(json.dumps({'ok': False, 'reason': 'no_llm_key'}).encode()); return
            try:
                res = llm_analyze(
                    params.get('url', [''])[0], params.get('kw', [''])[0],
                    params.get('sector', [''])[0], params.get('m', ['global'])[0],
                    params.get('pos', ['0'])[0], params.get('aov', ['0'])[0],
                    params.get('cur', [''])[0], params.get('lang', ['en'])[0],
                    do_crawl=(params.get('crawl', ['1'])[0] != '0'), premium=True)
            except Exception as e:
                print(f"⚠️  llm_analyze error: {e}")
                res = {'ok': False, 'reason': 'analyze_failed'}
            if res.get('ok'):
                # persist the FULL record (incl. private consultant_brief) for the dashboard
                store_audit({
                    'ts': time.strftime('%Y-%m-%d %H:%M'),
                    'name': params.get('name', [''])[0][:120],
                    'email': params.get('email', [''])[0][:160],
                    'url': params.get('url', [''])[0], 'keyword': params.get('kw', [''])[0],
                    'sector': params.get('sector', [''])[0], 'market': params.get('m', ['global'])[0],
                    'position': params.get('pos', ['0'])[0], 'crawled': res.get('crawled', False),
                    'analysis': res.get('analysis', {}),
                })
                # strip the private brief before sending to the CLIENT browser
                res = dict(res)
                ca = dict(res.get('analysis', {})); ca.pop('consultant_brief', None)
                res['analysis'] = ca
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode()); return
        if parsed.path == '/search' and 'q' in params and 'site' in params:
            q = params['q'][0]
            site = params['site'][0]
            market = params.get('m', ['global'])[0]
            try:
                result = search_google(q, site, market)
            except Exception as e:
                # DataForSEO down / timeout / bad creds — degrade gracefully with valid JSON
                # (the front-end keeps its sector estimate when found is false)
                print(f"⚠️  search_google error: {e}")
                result = {'position': None, 'found': False, 'source': 'estimation', 'error': 'search_unavailable'}
            self.wfile.write(json.dumps(result).encode())
        else:
            self.wfile.write(json.dumps({'error': 'Usage: /search?q=keyword&site=domain.com&m=global'}).encode())

if __name__ == '__main__':
    port = 8083
    # Bind loopback only — public access goes through the nginx reverse proxy (/flyer/api/search)
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f"✅ DataForSEO Search API running on 127.0.0.1:{port} (via nginx /flyer/api/search)")
    sync_dfs_balance()  # sync real balance from the free user_data endpoint → live counter starts from truth
    server.serve_forever()
