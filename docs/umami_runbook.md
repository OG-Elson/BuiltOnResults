# Runbook — Umami Analytics (BuiltOnResults) — 2026-07-16

> Décisions : Umami self-hosté, **bare Node + systemd** (pas Docker), **réutilise le MySQL maison** (bare-metal partagé : tradehub, afronmade_trader, etc.), sous-domaine `analytics.builtonresults.co.ke`.
> Serveur : Hetzner, 7.6 Go RAM / 4 cœurs / 96 Go libres / **0 swap** / Node 20.19.6 / MySQL 3306 / port **3001 libre** pour Umami.
> Légende : 🧑 = action OG-Elson (sudo/DNS) · 🤖 = action Claude.

## ⚙️ ÉTAT RÉEL (mis à jour 2026-07-16)
- ✅ **Phase 0** : swap 2G actif · DNS `analytics.builtonresults.co.ke` → 46.224.49.147 · base+user MySQL `umami` (connection string dans `~/.bor_analytics_db`).
- ⚠️ **Décision version** : Umami **v3 est Postgres-only** (a abandonné MySQL) → on a pris **Umami v2.20.2** (dernière v2 avec MySQL), pour réutiliser le MySQL maison. Choix validé par OG-Elson.
- ✅ **Phase 1** : Umami v2.20.2 installé dans `/home/deploy/umami` (pnpm 9.15.9 via corepack `~/.local/bin`), build OK (tables MySQL créées via migrations), tourne en **standalone** sur **127.0.0.1:3001** (loopback). Tracker `/script.js` → 200.
  - Lancé détaché : `setsid nohup env PORT=3001 HOSTNAME=127.0.0.1 … node .next/standalone/server.js`. Script de redémarrage : `/home/deploy/umami/run.sh`.
  - ⚠️ standalone : après un rebuild/upgrade, recopier `.next/static` → `.next/standalone/.next/static` (+ `public`).
- ✅ **Phase 2** : vhost nginx `analytics` + Certbot SSL (Let's Encrypt) → `https://analytics.builtonresults.co.ke` live.
- ✅ **Phase 3** : 2 sites créés (builtonresults.co.ke = `bf937960-b95a-4c84-b467-62f76cb830c4` · chefangela.co.ke = `4415c708-2f0f-41bf-9492-db8859837355`). Snippet injecté dans les 7 pages BuiltOnResults + index insights. Mot de passe admin changé (dans `~/.bor_analytics`) ; helper `~/umami-passwd.sh 'nouveau'` pour qu'OG-Elson le change lui-même.
  - **Events client** (ut() dans seo-audit.html/consultation.html) : `paid_cta_click`, `checkout_channel`, `checkout_claim`, `free_lead`, `consultation_submit`.
  - **Events serveur** (`umami_track()` dans search_api.py, via `/api/send`) : `paid_success`, `brief_received`, `brief_qualified`, `brief_declined`.
  - ⚠️ **GOTCHA** : Umami **droppe les events dont le User-Agent n'est pas un navigateur** (filtre bot). Le helper serveur DOIT envoyer un UA Chrome réel (sinon 200 mais event non enregistré). Bonus : ça exclut aussi les robots automatiquement (rien à configurer).
  - Exclusion IP : `IGNORE_IP` non configuré (ne PAS y mettre l'IP serveur = elle porte les events serveur). Ajouter l'IP navigation d'OG-Elson quand il la donne.
- ✅ **Phase 4a** : backup nocturne `~/umami-backup.sh` (cron 03:00, gardé 14j, dumps dans `~/umami_backups/`).
- 🔄 **Phase 4b** (systemd, survie reboot) = 🧑 dernière étape sudo (unit fournie).

### Redémarrer Umami manuellement (si besoin)
`setsid nohup /home/deploy/umami/run.sh </dev/null >/home/deploy/umami/umami.log 2>&1 & disown` (après avoir kill l'ancien process sur :3001).

---

## Phase 0 — Prérequis (🧑, à faire en premier)

### 0a. Swap 2 Go (garde-fou OOM — Chrome PDF + Umami)
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h   # vérifier : Swap 2.0Gi
```

### 0b. DNS (chez HostAfrica)
Créer un enregistrement **A** : `analytics` → **la même IPv4 que `builtonresults.co.ke`** (copier la valeur de l'A record existant). (AAAA IPv6 optionnel : `2a01:4f8:1c1a:feff::1`.)

### 0c. Base MySQL dédiée (isolée au niveau permissions)
```bash
sudo mysql
```
Puis coller (choisir un mot de passe fort, remplacer `CHANGE_ME`) :
```sql
CREATE DATABASE umami CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'umami'@'localhost' IDENTIFIED BY 'CHANGE_ME';
GRANT ALL PRIVILEGES ON umami.* TO 'umami'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```
Puis écrire la connection string dans un fichier lisible par `deploy` (hors git, convention `~/.bor_*`), pour que Claude configure Umami **sans que le secret transite par le channel** :
```bash
echo 'mysql://umami:CHANGE_ME@localhost:3306/umami' > ~/.bor_analytics_db
chmod 600 ~/.bor_analytics_db
```

---

## Phase 1 — Install + build Umami (🤖)
- Clone Umami (tag stable), `npm install`, générer `.env` : `DATABASE_URL` (lu depuis `~/.bor_analytics_db`) + `HASH_SALT` aléatoire + `PORT=3001` + `DISABLE_TELEMETRY=1`.
- `npm run build` (applique les migrations sur la base `umami`).
- Lancer détaché (comme le daemon Python) sur `127.0.0.1:3001` ; vérifier la réponse HTTP.

## Phase 2 — Exposition HTTPS (🧑, sudo)
Créer le vhost nginx (Claude fournit le fichier exact ci-dessous) puis Certbot :
```nginx
# /etc/nginx/sites-available/analytics
server {
  server_name analytics.builtonresults.co.ke;
  location / {
    proxy_pass http://127.0.0.1:3001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```
```bash
sudo ln -s /etc/nginx/sites-available/analytics /etc/nginx/sites-enabled/analytics
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d analytics.builtonresults.co.ke
```

## Phase 3 — Config tracking (🤖)
- Login Umami (défaut `admin` / `umami`) → **changer le mot de passe**, le stocker dans `~/.bor_analytics`.
- Créer 2 sites : `builtonresults.co.ke` + `chefangela.co.ke` → récupérer le `website-id`.
- Injecter le snippet `<script defer src="https://analytics.builtonresults.co.ke/script.js" data-website-id="…">` dans landing + `/audit` + `/consultation` + 4 articles. Redéployer.
- **Events client** (JS `umami.track()`) : `audit_landing_view`, `audit_paid_cta_click`, `audit_paid_channel_selected`.
- **Events serveur** (POST API Umami `/api/send` depuis `search_api.py`) : `audit_free_complete`, `paid_success` (chemin PayPal/M-Pesa magic-link seulement — Gumroad non webhooké), `audit_pdf_delivered`, `consultation_form_submit/qualified/declined`.
- `EXCLUDE_ROBOTS=true` + exclure l'IP d'OG-Elson.

## Phase 4 — Durcissement (🤖 + 🧑)
- 🤖 Backup : cron `mysqldump umami` (crontab deploy) vers le dossier de backup existant.
- 🧑 (recommandé) systemd unit pour Umami (survie au reboot) — Claude fournit le fichier `/etc/systemd/system/umami.service`.

---

## Ordre d'exécution
Phase 0 (🧑) → Phase 1 (🤖) → Phase 2 (🧑) → Phase 3 (🤖) → Phase 4. Chaque passage de main = un ping.

## Notes d'optimisation vs plan initial Cowork
- MySQL réutilisé (pas de conteneur Postgres) · bare systemd (pas de Docker) · swap ajouté · events serveur via API (pas seulement le snippet) · Clarity écarté (casse le privacy-first) · focus MVP sur 4 events funnel.
