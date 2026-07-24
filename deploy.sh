#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  deploy.sh — Deploy propre de BuiltOnResults (PROD)
#
#  Principe : WHITELIST EXPLICITE. Seuls les fichiers du site listés ci-dessous
#  sont publiés. Tout le reste (docs/, .git/, refs/, tests, *.py, PII outreach,
#  *.jsonl, prospects*.csv, caches, logs) est exclu PAR CONSTRUCTION — impossible
#  de fuiter par accident.
#
#  Transformations PROD (source utilise des chemins /flyer/ + builtonresults.com) :
#    /flyer/seo-audit-preview.html → /audit
#    /flyer/consultation.html      → /consultation
#    /flyer/…                      → /…          (api/search, insights/, images/)
#    builtonresults.com            → builtonresults.co.ke
#  Renommage fichier : seo-audit.html → audit.html
#  (seo-audit-preview.html = variante stale, NON déployée)
#
#  Usage :
#    ./deploy.sh <DEST>     # construit le site propre dans DEST
#    ./deploy.sh            # DEST par défaut = un dossier de staging (voir plus bas)
#
#  ⚠️ Ne déploie PAS directement sur la prod live : construit un arbre propre dans
#     DEST, à comparer (diff) puis à synchroniser vers la prod une fois validé.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SRC="/home/deploy/builtonresults"
DEST="${1:-/home/deploy/builtonresults/.deploy-staging}"

# ── Whitelist : fichiers du site à la racine ───────────────────────────────────
FILES=(
  index.html consultation.html audits.html seo-audit.html
  robots.txt sitemap.xml site.webmanifest
  favicon.ico favicon-16x16.png favicon-32x32.png apple-touch-icon.png
  android-chrome-192x192.png android-chrome-512x512.png
  logo-br.png "logo-br@2x.png" og-image.png
)
# ── Whitelist : dossiers copiés tels quels ─────────────────────────────────────
DIRS=( showcase images )
# insights/ : seuls les .html rendus sont publiés (les .md sont la source d'écriture)
# _send/    : loaders SANS PII (les vraies pages PII sont servies par le daemon)

echo "▶ Deploy propre → $DEST"
mkdir -p "$DEST"
# vide le CONTENU (pas le dossier lui-même : son parent peut être root-owned, ex. /var/www)
rm -rf "${DEST:?}"/* "${DEST:?}"/.[!.]* 2>/dev/null || true

# 1) fichiers racine
for f in "${FILES[@]}"; do cp "$SRC/$f" "$DEST/$f"; done

# 2) dossiers tels quels
for d in "${DIRS[@]}"; do cp -r "$SRC/$d" "$DEST/$d"; done

# 3) insights : seulement les .html
mkdir -p "$DEST/insights"
cp "$SRC/insights/"*.html "$DEST/insights/"

# 4) _send : loaders sans PII
mkdir -p "$DEST/_send"
cp "$SRC/_send/"*.html "$DEST/_send/"

# 5) renommage seo-audit.html → audit.html
mv "$DEST/seo-audit.html" "$DEST/audit.html"

# 6) réécritures PROD sur tous les .html (ordre important : URLs propres AVANT le /flyer/ générique)
find "$DEST" -name '*.html' -type f -print0 | while IFS= read -r -d '' h; do
  sed -i \
    -e 's#/flyer/seo-audit-preview\.html#/audit#g' \
    -e 's#/flyer/consultation\.html#/consultation#g' \
    -e 's#/seo-audit\.html#/audit#g' \
    -e 's#/flyer/#/#g' \
    -e 's#builtonresults\.com#builtonresults.co.ke#g' \
    "$h"
done

# 7) permissions lisibles par nginx (www-data)
chmod -R a+rX "$DEST"

echo "✔ Construit. Fichiers : $(find "$DEST" -type f | wc -l)"
echo "  Vérifier : aucune trace /flyer/ ou builtonresults.com, puis rsync vers la prod."
