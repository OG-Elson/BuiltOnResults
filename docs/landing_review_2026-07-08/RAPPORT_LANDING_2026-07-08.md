# Rapport visuel — Landing BUILTONRESULTS (état 2026-07-08)

**Auteur** : Cowork (via revue screenshots partagés par OG-Elson)
**Contexte** : landing générée via codedesign.ai (playground AI), URL preview `dev.codedesign.ai/playground-ai?id=cdgen_0c131be...`
**Screenshots joints** : 17 captures desktop (voir dossier `screenshots/`)
**Destinataire** : Claude Code (pour référence lors des optimisations en cours et à venir)

---

## 🎯 Vue d'ensemble

Landing consultante freelance web dev + SEO + workflow automation, positionnée sur le marché kényan. Style éditorial minimaliste, alternance sections claires/sombres, palette dominante coral/beige/black/cream. Header sticky avec nav SERVICES / PORTFOLIO / SKILLS / METHODOLOGY / FAQ + CTA orange "BOOK A CONSULTATION".

**Structure globale identifiée (17 sections dans l'ordre de scroll)** :

1. **Hero mosaic** — grid 8 images background (Nairobi cityscape / code / commerce local / GSC dashboard / homme portrait / ciel / restaurant meeting / panel coral) sans titre visible dans la partie haute
2. **Sub-hero** — texte "FREELANCE WEB DEVELOPMENT & SEO IN KENYA" superposé + typographie géante "BUILT ON RESULTS." dans un panneau coral droit
3. **Core Capabilities #1 — Web dev** — visuel écran de code + H2 "THE WEB DEVELOPMENT AND SEO CONSULTANTS." + 5 bullets (speed & conversion / SEO-GEO / workflow automation / digital strategy Kenyan market / technical audit)
4. **Performance by the numbers** — panneau coral + photo main + 4 KPIs : `45+` custom platforms, `180%` avg organic traffic growth, `2M` KES saved in overhead, `6 weeks` avg discovery-to-launch
5. **Core Capabilities #2 detail** — H2 "HIGH-PERFORMANCE DIGITAL ENGINEERING." + intro + 3 practices cards (01 WEB DEVELOPMENT / 02 SEO & GEO CONSULTING / 03 WORKFLOW AUTOMATION) avec CTA "VIEW PROJECTS →"
6. **Recent Insights** — grid 4 blog posts : "WHY STANDARD SEO FAILS IN THE KENYAN MARKET" (SEO & GEO, MAY 2026), "OPTIMIZING FOR M-PESA AND MOBILE-FIRST SPEEDS" (WEB DEV, APR 2026), "THE TRANSITION FROM SEARCH ENGINES TO AI ENGINES" (DIGITAL STRATEGY, MAR 2026), "SCALING CHEF ANGELA KENYA'S DIGITAL PRESENCE" (CASE STUDY, FEB 2026) — lien "ALL INSIGHTS →"
7. **Positioning duo** — bloc coral "ENGINEERED FOR THE KENYAN MARKET." + bloc noir "PERFORMANCE OVER PRESENTATIONS." (baseline anti-jargon, ROI-first)
8. **Manifesto** — panneau coral + photo minimaliste chaise/cadre + H2 "WE BUILD FOR PERFORMANCE, NOT TEMPLATES." + copy sur roster limité + engineering custom
9. **Industries served** — grid 8 secteurs verticaux avec icônes (E-COMMERCE & RETAIL / PROFESSIONAL SERVICES / HOSPITALITY & FOOD / REAL ESTATE / FINANCIAL SERVICES / LOGISTICS & TRANSPORT / EDUCATION & TRAINING / HEALTHCARE & WELLNESS)
10. **Our Process** — H2 "FROM DISCOVERY TO DEPLOYMENT, IN FOUR STEPS." + 4 étapes coral en pastilles : 01 AUDIT / 02 ARCHITECT / 03 BUILD / 04 LAUNCH
11. **Engineered for Growth (testimonials)** — bloc sombre + H2 "ENGINEERED FOR GROWTH." + 3 quotes clients : Angela Mwangi (Chef Angela Kenya — organic traffic doublé en 3 mois), David Ochieng (Tradehub — lead gen pipeline streamlined), Sarah Kamau (compliment tech dev + SEO)

---

## ✅ Ce qui fonctionne bien

- **Copywriting cohérent** : le fil rouge "performance / results / measurable / Kenyan market" est répété sans devenir redondant → positionnement clair vs concurrents génériques
- **KPI section** — 45+ / 180% / 2M KES / 6 weeks = benchmarks concrets, très bon pour la conversion (concrete over vague)
- **Testimonials cross-projects holding** — Chef Angela + Tradehub cités = social proof réel du portfolio OG-Elson, cohérent avec sa réalité de holding
- **Rythme visuel alternance clair/sombre** — évite la fatigue visuelle sur scroll long
- **Palette limitée à 4 couleurs** — coral #E8B598 approx, black, off-white/cream, wood beige → identité cohérente
- **Story arc bien construit** — Hero → What → How (process) → Proof (testimonials) = funnel classique éprouvé

---

## ⚠️ Points d'amélioration / observations pour Claude Code

### 1. Hero mosaic trop chargé (screen 1-2)
La grid 8 images en background sans H1 visible = **manque de focus au premier scroll**. Un visiteur qui arrive ne comprend pas immédiatement ce qui est proposé.

**Suggestion** :
- Ajouter un H1 court en overlay sur le hero mosaic dès le fold (ex : "Custom web platforms that convert. Built in Kenya.")
- OU réduire à 3-4 images clés (pas 8) pour aérer

### 2. "BUILT ON RESULTS" tronqué (screen 2)
Le titre principal "BUILT ON RESULTS." apparaît coupé en deux lignes séparées d'autres images. Sur mobile ce sera pire.

**Suggestion** : recomposer pour que le titre principal soit **d'un seul tenant** dans un bloc coral, sans image intercalée.

### 3. KPI section (screen 5-6) — cassée en scroll
Les 4 KPIs (45+ / 180% / 2M / 6 weeks) sont scindés visuellement entre 2 lignes dans l'affichage actuel. Sur desktop large ça passe, mais sur laptop 1440px c'est déjà borderline.

**Suggestion** : forcer `grid-cols-2 md:grid-cols-4` avec `gap` réduit pour tenir sur une seule ligne au-dessus de la breakpoint desktop.

### 4. "SCALING CHEF ANGELA KENYA'S DIGITAL PRESENCE" (screen 10)
Excellent choix de case study en featured post — c'est LA carte social proof la plus forte du portfolio holding. Mais l'image du post (cutting board close-up) est identique à d'autres shots food du site → peut créer confusion.

**Suggestion** :
- Utiliser une des nouvelles photos pro du shoot Chef Angela 04/07 (`dish 1.jpg` ou `chef 1.jpg` dans `projects/chef_angela/shoot_2026-07-04/content social media/`)
- Ça renforce la cohérence brand cross-projects holding

### 5. Testimonial Angela Mwangi vs Chef Angela Liyayi (screen 17)
Le testimonial cite "Angela Mwangi — Chef Angela Kenya" mais le nom réel est **Angela Liyayi** (Chef Angie). Divergence de patronyme à corriger, sinon c'est un red flag crédibilité.

**Suggestion** : vérifier avec OG-Elson quel est le patronyme corrigé + updater dans la génération codedesign.ai.

### 6. Manque de mention du SEO Audit Tool ($15 product)
Le SEO Audit tool que Hermes + Claude Code sont en train d'optimiser (task 07/07 sur le channel) **n'apparaît nulle part sur cette landing**. C'est pourtant un produit d'entrée gamme (lead magnet à $15) qui devrait avoir sa propre section ou CTA.

**Suggestion majeure** :
- Ajouter une section "Quick SEO Audit" avec CTA vers `/flyer/seo-audit.html` (déjà en prod)
- Positionnement : "Not sure where to start? Get a SEO audit report for $15" — lead magnet parfait pour convertir les visiteurs pas encore prêts à booker une consultation
- Utile pour **onboarder les prospects "cold"** avant book a consultation

### 7. Nav "SKILLS" vs "PORTFOLIO"
Les 2 sont proches sémantiquement. Skills = ce qu'on sait faire, Portfolio = ce qu'on a fait. Sur une landing consulting, un seul suffit habituellement.

**Suggestion** : envisager fusion en "PORTFOLIO" (le portfolio suggère implicitement les skills) OU renommer SKILLS en "APPROACH" / "PROCESS" (mais alors doublon avec METHODOLOGY).

### 8. Absence de pricing / packages
Il n'y a aucune indication de fourchette de prix, ce qui **augmente le taux de rebond des visiteurs mal qualifiés**.

**Suggestion** : ajouter au moins une fourchette indicative dans "Book a consultation" (ex : "Consultations starting at 30K KES / discovery call free") pour filtrer les leads.

---

## 🎨 Direction artistique — cohérence brand holding

La palette et le style éditorial sont **très différents** du reste du portfolio holding :
- Chef Angela = Coastal Chef Angie (ocean-dark #1B2F44 + coral #E07856 + sand-light + cream)
- BuiltOnResults = coral/salmon plus rosé + black + wood beige

**Question stratégique pour OG-Elson** : les 2 identités visuelles doivent-elles être proches (brand holding unifié) ou volontairement distinctes (agences séparées) ?

Recommandation Cowork : **volontairement distinctes** = OK (le client d'un consulting tech ≠ le client d'une chef privée), mais garder un "manifest holding" invisible = même typographie sans-serif, même approche éditoriale minimaliste.

---

## 📋 TL;DR pour Claude Code

**Priorités à traiter** (par ordre d'impact) :

1. **P1** — Ajouter H1 court dans le hero mosaic (fold), corriger cassure "BUILT ON RESULTS" tronqué
2. **P1** — Corriger nom testimonial "Angela Mwangi" → "Angela Liyayi" (Chef Angie)
3. **P2** — Ajouter section "Quick SEO Audit $15" avec CTA vers le tool déjà en prod (`/flyer/seo-audit.html`)
4. **P2** — Force KPI grid à 4 colonnes sur desktop
5. **P3** — Remplacer image case study Chef Angela par photo pro du shoot 04/07
6. **P3** — Fusionner SKILLS et PORTFOLIO OU renommer

**Aucune modif à faire sans go OG-Elson** — ce document est un rapport de revue, pas une TASK.

---

## 📁 Fichiers joints

Dossier `screenshots/` — 17 captures desktop numérotées `01_hero.png` à `17_testimonials.png` (à déposer par OG-Elson depuis son dossier Windows Screenshots).
