# Handoff Cowork → Claude Code — Décision infra BuiltOnResults + config domaine `builtonresults.co.ke`

**Date** : 2026-07-12
**From** : Cowork (session Opus 4.7)
**To** : Claude Code (Opus 4.8)
**Contexte** : reprise de la réflexion sur choix infra prod BuiltOnResults + setup DNS pour email Brevo + site

---

## 🎯 Décision à prendre

OG-Elson vient d'**acheter** le nom de domaine **`builtonresults.co.ke`** chez **HostAfrica** (même registrar que `chefangela.co.ke` pour centralisation panel DNS).

Il veut :
1. Servir le site en prod sur ce domaine (fin du `/flyer/builtonresults-preview.html`)
2. Envoyer des emails depuis ce domaine via **Brevo** (adresse expéditeur à décider : `hello@`, `contact@`, `elson@`)

**Question à trancher AVANT de configurer les DNS chez HostAfrica** :
👉 **Vercel ou Hetzner pour la prod ?**

Le pointage DNS est différent selon la réponse, donc décision à figer d'abord.

---

## 📊 État actuel

### Ce qui est en place

- **Serveur Hetzner** `46.224.49.147`, user `deploy`, SSH alias `tradehub`
- **Landing BuiltOnResults** : `/home/deploy/builtonresults/index.html` → servie via nginx sur `/var/www/flyer-gigs/out/builtonresults-preview.html`
- **Outil SEO Audit** : `/home/deploy/builtonresults/seo-audit.html` (frontend) + backend Python `search_api.py` (DataForSEO API + cache disque + optimistic UI + i18n) — tourne natif sur Hetzner via nginx proxy
- **4 articles Insights** : publiés en preview `/flyer/insights/*.html`
- **Design éditorial coral/cream** validé (voix « I », mobile-optimisé, scroll-reveal)

### Ce qui est décidé mais pas activé

Dans `agent-comms/channel.md` (2026-07-10), Hermes a acté :
> Plan déploiement : Vercel Option A (port du backend `search_api.py` en fonction serverless + Upstash) — **pas encore activé**

Donc le plan initial = Vercel avec refactor backend. Mais Cowork rouvre la question : est-ce toujours pertinent maintenant que le domaine est acheté et qu'on est prêt à basculer ?

---

## ⚖️ Trade-offs Hetzner vs Vercel

| Critère | **Hetzner** (setup actuel) | **Vercel** (plan initial Hermes) |
|---|---|---|
| Coût | Déjà payé, marginal (~5-10€/mo) | Free tier 100 GB/mo, Pro $20/mo |
| Landing statique | ✅ nginx trivial | ✅ deploy auto git push |
| Backend `search_api.py` Python | ✅ Tourne natif comme aujourd'hui | ❌ **Refactor requis** : port en Serverless Function + Upstash Redis pour remplacer le cache disque |
| Cache DataForSEO (aujourd'hui = disque) | ✅ Fichiers persistants | ❌ Nécessite Upstash Redis (free tier existe mais rate limits) |
| CDN mondial | ❌ Latence hors Europe | ✅ Edge network global |
| SSL | Let's Encrypt manuel (déjà fait pour `flyer-gigs`) | ✅ Auto par Vercel |
| Deploy | git pull + nginx reload | ✅ Auto sur git push |
| Preview par PR | ❌ | ✅ Auto |
| Uptime | Toi qui gères | ✅ Vercel SLA |
| Analytics | Nginx logs / manuel | ✅ Vercel Analytics intégré |
| Single point of failure | Oui (1 serveur) | Non (edge global) |
| Cohérence stack holding | Chef Angela = Vercel | ⭐ Uniformisation stack |

---

## 🎯 3 options en jeu

### Option A — Rester sur Hetzner
- Pointer `builtonresults.co.ke` en `A record` → `46.224.49.147`
- SSL Let's Encrypt via Certbot
- Aucun refactor. Backend Python fonctionne déjà.
- ⏱ Temps setup : ~30 min (DNS + Certbot + nginx server_name)
- Coût : 0 additionnel

### Option B — Migrer sur Vercel (plan Hermes activé)
- Refactor `search_api.py` → Serverless Function (Node ou Python selon feasibility Vercel)
- Migration cache disque → Upstash Redis (config secrets + code adapté)
- Pointer `builtonresults.co.ke` vers Vercel (A + CNAME)
- Chef Angela stack aligné
- ⏱ Temps setup : 2-4h Claude Code (refactor + tests + déploiement + DNS)
- Coût : 0-20€/mo Vercel + free Upstash tier

### Option C — Hybride
- Landing statique sur Vercel (deploy auto)
- Backend SEO Audit reste sur Hetzner via sous-domaine `api.builtonresults.co.ke` → CORS depuis Vercel
- ⏱ Temps setup : ~2h Claude Code (config Vercel + CORS + sous-domaine + tests)
- Coût : 0 additionnel
- Trade-off : 2 infra à maintenir + surface d'attaque CORS

---

## 💡 Avis Cowork (à challenger)

**Reco pragmatique = Option A pour l'instant** :
1. Pas encore de gros trafic (CDN mondial pas urgent)
2. Le refactor Vercel = 2-4h = friction MVP inutile
3. OG-Elson maîtrise déjà Hetzner (uniformité opérationnelle sur ce projet)
4. Migration vers B toujours possible plus tard (DNS = 15 min à changer, le refactor backend restera à faire de toute façon)

**Option B pertinente si** :
- Vision long terme "SaaS pro international" et on veut la stack pro dès maintenant
- Uniformisation stack holding (tout Vercel) = préférence stratégique

**Option C** = compromis technique élégant mais 2 infra à maintenir + config CORS sensible pour un solo freelance. À éviter probablement.

---

## 🔧 Ce qu'il faut décider avec OG-Elson

1. **Choix infra : A / B / C ?**
2. **Adresse email expéditeur Brevo** : `hello@`, `contact@`, `elson@` ?
3. **Réception email** (chantier séparé) : Google Workspace payant OU forwarder gratuit HostAfrica → Gmail ?
4. **Sous-domaines à prévoir** : `www.builtonresults.co.ke` (redirect vers apex ou inverse ?), `audit.builtonresults.co.ke` (outil SEO en sous-domaine dédié ?), autres ?

---

## 📋 Une fois décidé — chantier suivant

### Si A (Hetzner)
1. Nginx `server_name builtonresults.co.ke;` sur les blocs concernés (landing + `/audit`)
2. Certbot pour SSL sur le nouveau domaine
3. HostAfrica DNS : `A @` → `46.224.49.147`, `CNAME www` → `builtonresults.co.ke`
4. Brevo : ajouter le domaine, récupérer les valeurs DKIM/SPF/DMARC
5. HostAfrica DNS : ajouter les TXT/CNAME Brevo dans la même passe
6. Vérifier propagation avec `dig` + validation Brevo
7. Promouvoir `builtonresults-preview.html` → `index.html` sur nginx

### Si B (Vercel)
1. Refactor `search_api.py` en Serverless Function + Upstash Redis
2. Setup projet Vercel + import repo GitHub `OG-Elson-Private`
3. Config env vars Vercel (DataForSEO keys, Upstash URL)
4. HostAfrica DNS : `A @` → `76.76.21.21`, `CNAME www` → `cname.vercel-dns.com`
5. Brevo : mêmes records DNS TXT/CNAME dans la même passe
6. Deploy + tests + smoke tests

### Si C (Hybride)
1. Setup Vercel pour la landing (statique)
2. Config sous-domaine `api.builtonresults.co.ke` chez HostAfrica → `A` vers Hetzner
3. Adapter le fetch dans le frontend outil SEO pour taper `api.builtonresults.co.ke`
4. Config CORS côté nginx Hetzner pour autoriser origin Vercel
5. Tests

---

## 📎 Références vault utiles

- État actuel des chantiers : `agent-comms/channel.md` (surtout entrées 2026-07-10 CLAUDE-CODE et HERMES)
- Skill webdesigner (mobile-optim) : `/home/deploy/.hermes/skills/creative/webdesigner/SKILL.md`
- Skill copywriter_seo : `/home/deploy/.hermes/skills/creative/copywriter_seo/SKILL.md`
- Mémoire Cowork sur les registrars holding : centralisation HostAfrica pour tous les `.co.ke`
- PayPal handle actuel `builtonresult` (sans s) — sera renommé en `builtonresults` pour cohérence

---

## 🚦 Ce que je te demande

1. **Lire `agent-comms/channel.md`** pour reprendre le contexte complet
2. **Analyser les 3 options** avec OG-Elson (challenger mon avis A si tu vois mieux)
3. **Trancher** la décision infra
4. Une fois décidé : **dérouler le setup complet** (DNS HostAfrica + Brevo + éventuel refactor Vercel selon choix)
5. **REPORT dans `agent-comms/channel.md`** en fin de session : décision retenue + actions prises + prochaines étapes

Bonne réflexion 🎯
