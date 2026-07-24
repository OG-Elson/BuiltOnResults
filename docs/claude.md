# Projet — BuiltOnResults

> 📋 **Règles holding** — sommaire en tête de `/home/deploy/vault/CLAUDE.md` (parité mobile, aucune position financière, sync de clôture, mobiliser les ressources web).

## Contexte
Service de consulting digital freelance sous la marque **BuiltOnResults**.
Offre : **SEO (classement Google) + développement web + automation** — audit SEO gratuit (lead magnet) + audit $15 + offre sectorielle milestone (ex. cleaning 10k KES). Ancienne formulation (sites/branding/SaaS) élargie côté SEO-first.
Marché primaire : Kenya (PME, commerces locaux).
Extension prévue : international (Afrique de l'Est, puis global).

## Identité
- **Nom** : BuiltOnResults
- **Positionnement** : freelancer digital, pas agence
- **USP** : paiement par milestones — le client ne paye qu'aux objectifs atteints
- **Langue** : anglais uniquement
- **Tonalité** : professionnelle, directe, orientée résultats

## Domaines & réseaux
- **builtonresults.co.ke** ✅ LIVE (SSL + Umami) · sous-domaine `analytics.builtonresults.co.ke`
- builtonresults.com — statut à confirmer
- @builtonresults (Instagram / Facebook / LinkedIn…) — **à confirmer** (DONNÉE MANQUANTE)

## Stack technique — corrigé 2026-07-23
- **Front statique** (HTML/CSS/JS) + **daemon Python `search_api.py`** (`http.server`, `127.0.0.1:8083`) derrière **nginx** ; déploiement via `/var/www/flyer-gigs/`.
- Détail opérationnel (deploy, restart daemon, endpoints, secrets) : **`CLAUDE.md` à la racine du dossier serveur `/home/deploy/builtonresults/`** (auto-chargé en session).
- *(L'ancienne fiche « Next.js + Vercel, comme Chef Angela » était fausse — copiée par erreur, ce n'est pas ce qui tourne.)*

## Services — offre SEO-first (corrigé 2026-07-23)
1. **SEO** (classement Google) — cœur de l'offre
2. **Développement web** + **automation** (intégration M-Pesa, workflows)
3. **AEO / GEO** — optimisation pour les moteurs et les IA
- Entonnoir : **audit SEO gratuit** (`/audit`, lead magnet) → audit payant → offre sectorielle par **milestones**.
- *(L'ancienne formulation « sites / branding / SaaS » est dépassée depuis le pivot SEO-first.)*

## Modèle de pricing
- Devis au cas par cas (comprendre les besoins → définir les milestones → chiffrer)
- Paiement débloqué par milestone atteint
- Pas de grille de prix publique

## Structure site (décision : Option C — Funnel-oriented)
- Landing pages ciblées par service (1 page = 1 service)
- Page "How I work" (explique le modèle milestone payment)
- Portfolio / Case Studies
- CTA unique par page → booking call / formulaire contact

## Portfolio de lancement
- **Chef Angela** (site restaurant/hospitality, branding, Diani Beach)
- **Tradehub** (SaaS/app trading crypto)

## Stratégie d'acquisition
- **Canaux prioritaires** : Instagram + Facebook (contenu visuel, groupes business Kenya)
- **Cold outreach** : identifier PME sans site / avec site mauvais (restaurants, hôtels, shops)
- **LinkedIn** : phase 2, après premières missions sécurisées
- **Plateformes freelance africaines** : phase 3, indépendance d'abord

## Statut
🟢 **PHASE 1 — Build livré, outbound lancé** (depuis 2026-07-20). État vivant : `handoff.md` · verdict/faisabilité : `audit_etat_2026-07.md`.

### Roadmap Phase 0 (✅ terminée)
- [x] Domaine builtonresults.co.ke sécurisé + **site live** (SSL + Umami)
- [x] Site construit : landing + /audit (outil SEO) + /audits + /consultation + /insights (4 articles) + /showcase/cleaning-mombasa
- [ ] builtonresults.com + handles Instagram/Facebook — **à confirmer**
- [ ] Case study Chef Angela **chiffrée** — à publier (levier #2 de l'audit)

### Phase 1 en cours — acquisition
- **Outbound cleaning WhatsApp LANCÉ (2026-07-20)** : Batch 1 envoyé (GM/Ella/Maident), Batch 2 généré (~12), 1er lead chaud **Kejani (Kevin)**.
- Prochain : volume sur toute la liste (25) + case study Angela + fluidifier réponse→closing. Goulot = acquisition.

## Règles projet
- Ne pas lancer le site avant d'avoir au moins 1 case study complète
- Priorité absolue = terminer Chef Angela d'abord
- Budget : minimal (domaine ; hébergement **auto-hébergé sur le serveur Hetzner existant** derrière nginx — pas de Vercel, coût marginal nul)
