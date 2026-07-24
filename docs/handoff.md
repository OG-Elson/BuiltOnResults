# Handoff — BuiltOnResults

## Session 2026-07-24 — Réorganisation projet + plan d'acquisition

**A) Grand chantier de réorganisation du rangement (TERMINÉ).** Le projet était éparpillé sur
4 emplacements + squattait le repo Flyer_gigs + avait une expo PII sur le web. Corrigé :
- **Repo dédié** `github.com/OG-Elson/BuiltOnResults` (privé) — le code a enfin git/backup.
  Auth push : compte `OG-Elson` via token (`~/.bor_gh_token`, dans le credential store).
- **Docs** rapatriés dans le repo (`docs/`). Le **vault** ne garde qu'un **pointeur**
  (`projects/builtonresults/README.md`) + le channel. Modèle : vault = coordination inter-agent
  seulement ; chaque projet = son repo (comme Chef Angela).
- **Sensible → Drive** : `prospects_cote_mombasa.csv` → **Sheet Google éditable**
  « BuiltOnResults — Prospects (Mombasa) » (dossier Drive « BuiltOnResults — Data & Sensible »).
  Le CSV/leads restent hors versionnement (`~/builtonresults_data/`). leads/audits déjà
  consultables via le **backoffice** `audits.html` (code admin `~/.bor_admin`).
- **Expo PII fermée** : les pages `_send/` (numéros prospects) étaient servies en clair. Désormais
  gétées par le **code admin** via le daemon (`fn=send_tool`, lit `~/builtonresults_data/_send_tool/`,
  hors web-root) ; les pages publiques `/_send/` sont des **loaders** sans PII.
- **Deploy propre** : `deploy.sh` (repo) — whitelist explicite (impossible de publier docs/.git/PII),
  renomme `seo-audit.html`→`audit.html`, réécrit `/flyer/`→propre + `.com`→`.co.ke`. Validé
  byte-identique à la prod.
- **Nginx dé-squatté** : docroot basculé de `/var/www/flyer-gigs/builtonresults-prod` →
  **`/var/www/builtonresults`** (backup `builtonresults.bak-4d`). Live vérifié OK.
- ⚠️ **Reste optionnel** : purger l'ancien `/var/www/flyer-gigs/{builtonresults-prod,out}` (plus servis).
- ⚠️ `seo-audit-preview.html` dans le repo = **variante stale**, NON déployée (la vraie source = `seo-audit.html`).

**B) Plan d'acquisition social (validé, pas encore exécuté).** Direction A : **social d'abord**
(Facebook + Instagram), 3 axes (social / site-SEO / outbound). Plans dans `docs/` :
`plan_acquisition_social_2026-07.md` (cadre) + `plan_acquisition_semaine0_2026-07.md` (actions 0€-first :
créer IG/FB, bios rédigées, carrousels, gate → audit gratuit). Décisions actées : faceless, anglais,
10-20h/sem, boost au besoin. **En attente** : recherche outil **Polo AI** (via Hermes) + **chiffres
case study Angela** + création des comptes IG/FB (action OG-Elson). Logo profil prêt :
`docs/assets/br_avatar_512.png`.

## Dernière session : 2026-07-20

## État actuel
🟢 **PHASE 1 — actif construit, outbound LANCÉ (2026-07-20)**

> Corrigé le 2026-07-20 : la version précédente (2026-06-24) affirmait « aucun domaine ni handle
> sécurisé », ce qui était faux depuis le 16/07. Un handoff périmé fait démarrer les audits sur
> une fausse base — vérifier avant de s'y fier.

- Domaine `builtonresults.co.ke` **live + SSL** ; sous-domaine analytics Umami opérationnel.
- Site : landing + `/audit` (outil SEO fonctionnel) + `/audits` + `/consultation` +
  `/insights` (4 articles) + `/showcase/cleaning-mombasa`.
- Positionnement : freelance solo, « Based in Kenya · Remote worldwide », SEO + dev web +
  automation. Produit d'entrée : audit payant + audit gratuit en lead magnet. Offre cleaning
  en paliers (pay-on-milestone), inversion du risque.
- Prospection : moteur en place + **25 contacts qualifiés** (CSV) + surplus réutilisable du cache SERP ($0). **Outreach cleaning LANCÉ 2026-07-20** : Batch 1 envoyé (GM/Ella/Maident), Batch 2 généré (~12). 1ères réponses : Top Kick = pas intéressé, **Kejani (Kevin) = 1er lead chaud**.
- Trafic organique ≈ **0** (normal, site à ~4 jours) — l'acquisition passe par l'outbound, tout juste lancé. Ce n'est pas un problème de conversion.

**Prochaine étape unique** : envoyer l'outbound à volume + publier la case study Chef Angela
chiffrée.

**Critère de pivot acté** : 0 encaissé au 30/09 malgré ≥80 contactés et ≥3 conversations réelles
→ pivot (canal, secteur ou offre).

Audit complet : `projects/builtonresults/audit_etat_2026-07.md`. Engagements suivis dans l'onglet
`Taches` du Sheet.

## Décisions prises (2026-06-24) — instantané historique

> ⚠️ **Snapshot de lancement, deux points ont depuis évolué** (voir `claude.md` à jour) : le **3**
> (services) et le **8** (stack). Ne pas s'y fier tels quels.

1. **Nom** : BuiltOnResults — vérifié exhaustivement (domaines .com/.co.ke/.io/.africa/.digital tous disponibles, handles sociaux libres, aucune marque déposée, aucune entreprise existante)
2. **Positionnement** : freelancer digital (pas agence), paiement par milestones
3. ~~Services : sites web + branding + SaaS~~ → **PIVOT SEO-first** (2026-07) : SEO + dev web + automation + AEO/GEO. Voir `claude.md`.
4. **Structure site** : Option C (funnel-oriented) — 1 landing par service + page "How I work" + portfolio
5. **Canaux acquisition** : Instagram + Facebook d'abord, LinkedIn après premières missions, plateformes freelance = phase 3
6. **Pricing** : devis au cas par cas, pas de grille publique
7. **Langue** : anglais uniquement
8. ~~Stack : même que Chef Angela (Next.js + Vercel)~~ → **FAUX/PÉRIMÉ** : réel = front statique + daemon Python `search_api.py` + nginx. Voir `CLAUDE.md` serveur.
9. **Portfolio** : Chef Angela + Tradehub comme case studies
10. **Séquence** : finir branding Chef Angela AVANT de construire le site BuiltOnResults

## Prochaines actions — plan pré-lancement du 2026-06-24 (SUPERSEDED)

> ⚠️ Ces actions sont **faites ou dépassées** : `.co.ke` **live** depuis le 16/07, site construit,
> outbound lancé. L'**étape courante** est en tête de ce fichier (outbound à volume + case study
> Angela chiffrée). Bloc conservé pour trace, pas comme to-do.

1. ~~Sécuriser domaines~~ — `.co.ke` fait (live + SSL). Reste `.com` : statut à confirmer.
2. Réserver handles Instagram + Facebook @builtonresults — **encore à confirmer**.
3. ~~Continuer branding Chef Angela~~ — Chef Angela avancé ; n'est plus un bloqueur.
4. ~~Explorer templates design~~ — dépassé (stack statique en place).

## Blocages
- Aucun bloquant technique.
- ~~Dépendance : branding Chef Angela avant Phase 1~~ — **levée**, Phase 1 déjà lancée (outbound).

## Noms alternatifs rejetés
- ResultFirst : ❌ marque déposée USPTO, entreprise 150+ employés
- Craftiq : ❌ 17+ entreprises, domaines saturés
- Mwanga Digital : ⚠️ .com pris (page parkée), viable mais moins propre
- ProveFirst : ✅ disponible (backup si besoin)
- MatokeoDigital : ✅ disponible (backup si besoin)
