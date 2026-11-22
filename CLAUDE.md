# CLAUDE.md — BuiltOnResults (contexte auto-chargé)

> 📋 **Règles holding** — sommaire en tête de `/home/deploy/vault/CLAUDE.md` (parité mobile, aucune position financière, sync de clôture, mobiliser les ressources web).

> Tu (Claude Code) démarres une session dédiée à **BuiltOnResults** (dossier de travail `/home/deploy/builtonresults/`, mémoire vierge — c'est voulu, pour ne PAS mélanger avec Chef Angela). **Lis ce fichier en entier avant d'agir.**
> Note : jusqu'à mi-07/2026 le travail BuiltOnResults tournait sous le projet `-var-www-chef-angela` (cwd mélangé) — d'où ce fichier pour repartir propre.

> 🗣️ **Language (decided 2026-08-05) — ENGLISH by default, everywhere.** Everything Claude Code **generates or writes** for BuiltOnResults is in **English**: direct replies, docs/files, and channel messages emitted by [BuiltOnResults]. **No gradual switch.** Only exception: if OG-Elson explicitly asks for French. Don't retroactively rewrite other sessions' messages or pre-existing FR docs unless asked.

---

## 1. Le projet
**BuiltOnResults** = practice freelance **solo** d'OG-Elson (« Elson ») : **SEO + développement web** (+ AEO/GEO, M-Pesa integration, automation). Site : **builtonresults.co.ke** (live).
- **Positionnement (RÈGLE)** : voix **« I »** au singulier, **« Consultant »** (pas Consultants), **pas une agence**. Marché **Kenya-primary MAIS international** : « **based in Kenya, delivered worldwide** » — ne JAMAIS enfermer sur le Kenya. La formule « for the Kenyan market » seule = trop limitante → toujours l'associer à « and clients worldwide ». Mot-clé signature = `seo services kenya`.

## 2. Architecture & déploiement (⚠️ opérationnel — à respecter)
- **Front statique** (HTML/CSS/JS) + **daemon Python `search_api.py`** (`http.server`, single-thread, **127.0.0.1:8083**) derrière **nginx**.
- ⚠️ **nginx = exact match `= /api/search`** → TOUS les endpoints passent par ce path + `?fn=<name>`. Ajouter un nouveau path `/api/xxx` = modif nginx root (**sudo OG-Elson**).
- **Deploy** : source `/home/deploy/builtonresults/*` →
  - **preview** `/var/www/flyer-gigs/out/` (garde les chemins `/flyer/`)
  - **prod** `/var/www/builtonresults/` (corrected 2026-11-22; the old `/var/www/flyer-gigs/builtonresults-prod/` no longer exists). Build with `./deploy.sh <DEST>` (whitelist, default DEST = `.deploy-staging/`), diff, then sync to prod. Transformations applied by deploy.sh (`sed` : `/flyer/api/search`→`/api/search` · `/flyer/seo-audit-preview.html`→`/audit` · `/flyer/consultation.html`→`/consultation` · `/flyer/insights/`→`/insights/` · `/flyer/images/`→`/images/` · `builtonresults.com`→`builtonresults.co.ke`)
- **Restart daemon** (JAMAIS `pkill` — a tué le shell) :
  ```bash
  PID=$(ss -ltnp 2>/dev/null | grep ':8083' | grep -oP 'pid=\K[0-9]+' | head -1); [ -n "$PID" ] && kill $PID; sleep 1
  setsid nohup python3 /home/deploy/builtonresults/search_api.py </dev/null >/home/deploy/builtonresults/daemon.log 2>&1 & disown
  ```
- **Secrets** hors git : `~/.bor_*` (unlock, admin, email, mpesa, secret HMAC, analytics, analytics_db). **Data** : `~/builtonresults_data/*.jsonl` (audits, leads, pending_*). Ne jamais mettre de secret dans le channel.
- `search_api.py` s'importe en Python (pour tester des fonctions) avec `PYTHONPATH=/home/deploy/builtonresults` ou `cd` dedans.

## 3. Outils / assets clés
- **Outil d'audit SEO gratuit** (`/audit`) : crawl serveur + scorecard on-page + concurrents SERP + estimation revenus. **Audit payant $15** (Gumroad **`https://elsongster.gumroad.com/l/seo-audit`** LIVE + PayPal + M-Pesa magic-link) → LLM DeepSeek + DataForSEO premium → PDF Chrome headless + email Brevo.
- **DataForSEO** (API prépayée — **coûte des crédits, demander avant les gros pulls**) : `search_google(q, site, market, depth)`, `dataforseo_volumes(kws, market)`, `dataforseo_ranked(site, market)`. Marché Kenya = `africa` (2404). SERP ~$0.002 · premium (volumes $0.05 + ranked) ~$0.06–0.15/audit. **Solde réel ≈ $0.06 (le $1 offert est ~épuisé, min recharge $50).**
  - ⚠️ **PRÉ-VOL OBLIGATOIRE** : avant toute tâche DataForSEO, lire `~/builtonresults_data/dfs_budget.json` (compteur en direct) ; en début de session, vérifier le drapeau `~/builtonresults_data/DFS_LOW_BALANCE` (créé si solde bas) et prévenir OG-Elson. Chaque appel payant est loggé dans `usage.jsonl`. Tests **toujours** avec `MOCK=1`. Stratégie recharge : valider la demande gratuitement d'abord (voir memory `mvp-validation-recharge-strategy`).
- **Moteur de prospection** : `prospect_engine.py` (SERP pos 11-30 + crawl → CSV `{secteur,domaine,position,3 problèmes,contact,accroche}`). **Cache SERP** dans `.serp_cache/` → re-filtrer = $0.
- **Showcase templates** (démos pour outreach) : `showcase/cleaning-mombasa.html` → live `/showcase/cleaning-mombasa`. Statique + SEO + schema. (Autres secteurs à faire.)
- **Umami analytics** : `analytics.builtonresults.co.ke` (self-hosté systemd — voir `vault/projects/builtonresults/umami_runbook.md`). Events funnel client+serveur.
- **Brevo** email (`noreply@builtonresults.co.ke`), **email pro** `contact@builtonresults.co.ke` (ImprovMX + Brevo Send As).

## 4. État d'avancement (roadmap SEO)
- **Étape 1 — On-page** ✅ : landing optimisée (`seo services kenya`) + 4 articles (chacun 1 mot-clé/pilier).
- **Étape 2 — Fondations + indexation** ✅ : sitemap/robots/canonicals, **GSC vérifié** (sitemap soumis, 7 URLs indexées, **#2 sur le brand en <24h**), **GBP** créé, **Umami** installé.
- **Étape 3 — Autorité & backlinks** 🔄 EN COURS : tracker + copy kit dans le vault. **Blockers** : pas d'adresse Kenya (Tier 1 annuaires bloqués), backlink dofollow payant, track record vide. → pivot **prospection outbound + showcase templates**.

## 5. Travail actif / prochaines étapes
- 🔄 **PIVOT Nov 2026 (current priority)**: agent/platform-per-niche model + social promotion, value-first **Chef Angela story series** (8 episodes; Ep1 live 2026-11-20, Ep2 2026-11-22). Read first: the banner at the top of `vault/projects/builtonresults/handoff.md`, then `pivot_agent_model_framework_2026-11.md`, `social_launch_sprint_2026-11.md` (§6b Meta posting pipeline), `angela_story_series_2026-11.md`. Reels + posting tool: `/home/deploy/vault-media/builtonresults/reels/` (`publish.py`, nothing posted without OG-Elson's explicit "post"). The cleaning outreach below is the July track (on hold since the pivot unless OG-Elson resumes it).
- **Outreach prospects cleaning (Mombasa)** — ⚠️ **LANCÉ le 2026-07-20** (Batch 1 envoyé, 1er lead chaud **Kejani/Kevin**). État vivant : `vault/projects/builtonresults/handoff.md` + Sheet `Taches`. Prochain : **volume sur toute la liste (25)** + **case study Angela chiffrée** + **fluidifier réponse→closing**. Point encore à durcir = **l'OFFRE** (track-record-first, prix cassé 3 premiers, inversion du risque — skill `marketeur`). **Goulot = acquisition**, pas conversion. CSV : `vault/projects/builtonresults/prospects_cote_mombasa.csv`.
- **Showcase templates autres secteurs** (légal, dental) : réutiliser le pattern de `cleaning-mombasa.html`. Sources design : Hermes (brief dans `refs/inspiration/`), headless Chrome, ou codedesign.ai (**réservé aux vrais clients**, 2 gens restantes).
- **Pipeline screenshots** (ma vision) : OG-Elson dépose des images dans `/home/deploy/agent-comms/screenshots/` → je les lis (Read rend les PNG/JPG).

## 6. Vault, channel & conventions (⚠️ mémoire vierge — tout est ici)
- **Vault** `/home/deploy/vault/` (repo git, remote `github-vault:ElsongMaster/HoldingVault.git`). Commit comme **`OG-Elson <elsongmaster@gmail.com>`**, **AUCUNE signature Claude**. `git pull --rebase --autostash` PUIS push.
- **Channel** `/home/deploy/vault/agent-comms/channel.md` (coordination Cowork/Hermes). Lis + réponds. **Zéro secret dans le channel.**
- **Skills INDEX (obligatoire)** : `/home/deploy/vault/skills/INDEX.md` à consulter EN PREMIER. Pertinents ici : **`seo_expert`**, **`copywriter_seo`** (articles), **`marketeur`** (offre/funnel), **`web_analytics_setter`**, **`email_pro_setup`**.
- **Demander AVANT toute tâche qui consomme des crédits** (DataForSEO…) — valider params avec OG-Elson.
- **Livrables pour OG-Elson** → dans le **vault** (il `git pull`) ou un dossier serveur ouvert en **VSCode**. Le dossier `builtonresults/` **n'est PAS un repo git** (pas pullable — passe par le vault).
- **Docs de référence BuiltOnResults** (vault) : `projects/builtonresults/` → `claude.md`, `handoff.md` (état vivant), `audit_etat_2026-07.md` (faisabilité), `seo_report_2026-07.md`, `umami_runbook.md`, `backlink_copy_kit.md`, `etape3_backlinks_tracker.md`, `prompts/`, `prospects_cote_mombasa.csv`.
- **Dashboard de pilotage** : les engagements BuiltOnResults sont suivis dans le Sheet **`OGE_Dashboard_Data`**, onglet **`Taches`** (ex. T03 handles réseaux, T05 case study Angela, T07 prospects contactés, T18–T23 outreach/sourcing). Le dashboard web (`oge-pilotage.duckdns.org`) lit ce Sheet en direct. **Pour mettre à jour le Sheet** : suivre le skill **`pilotage_projets`** → `references/spec-maj-quotidienne.md` (limites d'écriture par colonne, pièges de locale fr_FR, ne jamais écrire dans une formule).

## 7. Ta première action
1. Lis ce fichier + le **channel** (dernières entrées) + le **skills INDEX**.
2. Reprends le fil actif (section 5) : si OG-Elson veut avancer sur l'**outreach cleaning**, commence par **caler l'OFFRE irrésistible** avec lui (skill `marketeur`), puis les **templates de messages**, puis il lance le batch.
3. Toute décision qui consomme des crédits ou consequente → **valide avec OG-Elson d'abord**.
