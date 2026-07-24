# Rapport visuel — SEO Audit Express (état 2026-07-08)

**Auteur** : Cowork (via revue screenshots partagés par OG-Elson)
**Contexte** : nouvelle landing générée via codedesign.ai (playground AI) — variante SEO Audit Tool
**Screenshots joints** : 25 captures desktop dans ce dossier
**Destinataire** : Claude Code (référence pour discussion positionnement + prochaine itération design)

---

## 🎯 Priorité #1 exprimée par OG-Elson

> "Reproduire un design soigné comme celui-là, après le contenu je m'en occuperai après."

**Objectif** = capturer et répliquer l'**esthétique éditoriale premium** de cette landing (serif italic géant, palette crème warm, gradient cards, trust bar) sur le tool SEO Audit actuellement en prod (`/flyer/seo-audit.html`). Le copy et positionnement seront ajustés dans une seconde passe.

**Focus Claude Code** : structure HTML + palette + typographie + micro-interactions. Pas le contenu textuel (sauf corrections évidentes = artefacts codedesign.ai listés plus bas).

---

## 🎯 Vue d'ensemble — surprise structurelle

Ce n'est **PAS le même site que BUILTONRESULTS**. C'est une **variante concurrente / test A** générée en parallèle :

| Dimension | BUILTONRESULTS | SEO Audit Express |
|---|---|---|
| **Marché cible** | Kenya (Nairobi, Diani...) | **Bruxelles / Belgique** ("eight major business sectors in Brussels and beyond") |
| **Business model** | Multi-service consulting (dev + SEO + workflow) | **Single-product** ($15 audit + upsell premium) |
| **Palette** | Coral #F0A78D + black + wood beige | Crème warm + black + serif italic gray + gradient cards |
| **Ton** | "Engineered for the Kenyan Market" | "Stop losing traffic to competitors" (pain point direct) |
| **CTA principal** | "BOOK A CONSULTATION" | "Calculate my potential" |
| **Nav** | SERVICES / PORTFOLIO / SKILLS / METHODOLOGY / FAQ | CTR Calculator / Revenue Loss / Action Plan / Full Audit / Case Study |

**Question stratégique clé pour OG-Elson** : c'est deux offres holding distinctes (Kenya vs Belgique), un test A/B de positionnement, ou une hallucination de codedesign.ai ?

---

## 🎨 Design & typographie

- **Hero H1** : Serif géant italic pour "How much does it cost to NOT be #1 on Google?" → très éditorial, ton premium magazine
- **Body** : Sans-serif classique, contraste fort avec le serif titre
- **Cards** : gradients colorés (jaune-rose / vert / bleu-violet) sur les 3 étapes du process
- **Icons** : minimalistes noir dans carrés arrondis blancs → cohérent avec le style éditorial
- **Trust bar** : "Based on real Google CTR data · No registration required · Instant results" → bonne réassurance

**Overall** : très pro, palette premium, aesthetic proche de Stripe / Linear / Vercel = signal "SaaS moderne" (vs BuiltOnResults qui a un aesthetic "agence dev").

---

## 🎯 Value proposition (points forts)

1. **Pain point hyper direct** — "How much does it cost to NOT be #1 on Google?" → question qui pique
2. **Résultat instantané promis** — "< 45s" audit speed
3. **Value ladder claire** :
   - Free : CTR calculator (lead capture)
   - $15 : Audit express (paid lead magnet)
   - Premium deep-dive : 7 additional checks (upsell)
4. **Metrics de trust** : "99.4% CTR accuracy" (source data), "+$350/mo" ROI typique
5. **Process en 3 étapes très clair** : Enter details → Analyze gap → Get action plan

---

## ⚠️ Anomalies détectées (ordre de gravité)

### 🔴 CRITIQUE — Mockup `driftline.io` hors-sujet
Un des screenshots montre une carte visuelle avec `app.driftline.io/inbox/Q3-reporting` et un contenu "Reporting permission errors broke our finance handoff & flagged in Q3 review" — **rien à voir avec du SEO**.

C'est probablement une **hallucination du builder codedesign.ai** qui a inséré un mockup générique de style "modern SaaS dashboard" en mode filler.

**Action** : à supprimer ou remplacer par une vraie capture du calculateur SEO Audit Express en action (ou d'un vrai rapport d'audit).

### 🟠 IMPORTANT — Contradiction "AUDIT SPEED < 45s"
La landing claim `< 45s` pour l'audit. Or Hermes + Claude Code sont en train d'optimiser le bouton "Calculate" **actuellement à 5-10s** (TASK 07/07 dans `agent-comms/channel.md`).

**Action** :
- Soit garder `< 45s` comme cible business et laisser Claude Code terminer l'optim
- Soit ajuster la claim à `Instant` ou `< 10s` si l'optim ne descendra pas assez bas
- Le fait de claim `< 45s` = OK vu la performance actuelle 5-10s = **on est bien en-dessous** ✅

### 🟡 À CORRIGER — Copy "Brussels" = artefact prompt AI, pas décision business
- Copy explicite : "eight major business sectors in **Brussels and beyond**" → **NE REFLÈTE PAS L'INTENTION BUSINESS**
- **Décision OG-Elson (2026-07-08)** : l'outil SEO Audit est un produit **GÉNÉRAL / worldwide** — pas ciblé Bruxelles. La mention "Brussels" vient d'un critère laissé dans le prompt codedesign.ai qui sera retiré via Claude Code.

**Action Claude Code** :
- Retirer toutes mentions "Brussels" du copy
- Reformuler en positionnement **global / neutre** (ex : "eight major business sectors worldwide" ou juste "across every industry")
- Éviter tout ancrage géographique qui limiterait le marché adressable

### 🟡 À VÉRIFIER — Nav item "Full Audit" et "Case Study"
Sont probablement des **placeholders vides** générés par le AI builder. À remplir avec du vrai contenu (page /full-audit avec les 7 checks du premium, page /case-study avec un vrai cas client).

### 🟢 SUGGESTION — Pricing $15
- $15 = très bon lead magnet (barrière d'entrée basse)
- Mais peut casser le **perceived value** (trop cheap = pas sérieux ?)
- Concurrents comparables : `SEOquake` (free), `SurferSEO audit` (part de $89/mo), `Ahrefs Site Audit` (part de $99/mo)

**Alternative à considérer** :
- **$19** ou **$29** = même barrière d'entrée mais perceived value up
- OU garder $15 mais **positionner comme "starter" + upsell $99 report complet**

### 🟢 SUGGESTION — Nom "SEO Audit Express"
- Fonctionnel mais générique → 200+ concurrents avec noms similaires
- Alternative : **"RankLoss"** (matche le pain point) / **"Position0"** / **"CTRCalculator.io"** — plus mémorables

---

## 📊 Recommandations Cowork pour Claude Code

### Immédiat (avant next boost/traffic)
1. **Supprimer le mockup `driftline.io`** — remplacer par vraie capture calculator
2. **Vérifier tous les H1/H2 et copy** pour éliminer les autres possibles hallucinations codedesign.ai
3. **Valider avec OG-Elson** le positionnement géo (Brussels vs Kenya vs les 2)

### Moyen terme
4. **Créer /case-study** avec un vrai cas client (idéalement Chef Angela — le lien BUILTONRESULTS existe déjà, cross-pollinisation cross-holding)
5. **Créer /full-audit** avec le détail des 7 checks premium (upsell page)
6. **Aligner claim "< 45s"** avec la performance réelle post-optim (Hermes en cours)

### Long terme
7. **A/B tester** $15 vs $19 vs $29 pricing (perceived value vs conversion)
8. **A/B tester** SEO Audit Express vs autre nom plus mémorable
9. **Décider stratégie holding** : SEO Audit Express + BUILTONRESULTS = deux marques distinctes ou fusion ?

---

## 🔗 Cross-références

- Landing BUILTONRESULTS review : `../RAPPORT_LANDING_2026-07-08.md`
- Task optim SEO Audit tool (Hermes → Claude Code) : `agent-comms/channel.md` [2026-07-07 19:30]
- Skill SEO Expert du vault : `skills/seo_expert/SKILL.md`

---

## 📎 Note importante

**Aucune modif à faire sans go OG-Elson** — ce document est une revue de discussion, pas une TASK exécutable. Les décisions de positionnement géo, pricing, et cohérence brand doivent venir du user.
