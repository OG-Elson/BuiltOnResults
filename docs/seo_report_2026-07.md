# BuiltOnResults — Rapport SEO (état au 2026-07-15)

> Rapport exhaustif de tout le travail SEO réalisé sur builtonresults.co.ke à ce jour.
> Méthodo : skills [[seo_expert]] (v1.1) + [[copywriter_seo]]. Site = HTML statique + daemon Python derrière nginx.
> Mapping fichiers : source landing `/home/deploy/builtonresults/index.html` · articles servis `out/insights/*.html` (preview `/flyer/`) → `builtonresults-prod/insights/*.html` (prod, URLs propres) · specs articles `/home/deploy/builtonresults/insights/*.md`.

---

## 1. Contexte & positionnement

- **Solo freelance** — voix « I » au singulier, jamais « we »/« team ». « Consultant » (pas « Consultants »). Pas une agence.
- **Positionnement produit** : SEO en tête (mot-clé signature `seo services kenya` — ranker dessus = preuve de compétence), web development en 2e service, **automation IA prévue en phase 2**.
- **Marché** : **Kenya-primary MAIS international** — « based in Kenya, delivered remotely worldwide ». Ne jamais enfermer la value prop sur le Kenya seul (règle répétée par OG-Elson). Le mot-clé reste Kenya (pour ranker), le positionnement reste Kenya + monde.
- Détails durables : voir memory `builtonresults-positioning-copy`.

## 2. Méthodologie appliquée (2 principes clés)

1. **Optimiser le contenu on-page AVANT d'indexer.** Site neuf = aucune baseline à protéger. Indexer une page non optimisée = Google met en cache un snippet médiocre 4-8 semaines. Ordre correct : keyword research → on-page → PUIS indexation (GSC/sitemap/request indexing). → intégré dans seo_expert v1.1 (principe #10).
2. **Vérifier les VRAIS volumes avant de choisir les mots-clés** (DataForSEO, jamais deviner). Beaucoup de mots-clés « évidents » = 0 recherche. → seo_expert v1.1 (principe #11).

## 3. Keyword research (data réelle DataForSEO)

### Marché Kenya (services)
| Mot-clé | Vol/mo | CPC | Comp | Décision |
|---|---|---|---|---|
| web design kenya / website design kenya | 880 | $0.91 | low | secondaire (landing) |
| **seo services kenya** | 390 | **$2.13** | low | **PRIMAIRE landing** |
| web design nairobi / web designer nairobi | 320 / 210 | | low | pages ville (futur) |
| digital marketing kenya | 210 | | low | secondaire |
| M-Pesa API | 260 | **$11.99** | low | article 2 |
| payment gateway kenya | 210 | $4.33 | medium | article 2 (secondaire) |
| SEO in Kenya / seo kenya | 110 | $0.38 | low | article 1 |
| M-Pesa integration | 110 | $1.25 | low | article 2 (primaire) |
| ecommerce website kenya | 90 | $0.61 | medium | |

### Marché global (pièce internationale AI/GEO)
| Mot-clé | Vol/mo | CPC |
|---|---|---|
| ai seo | 8 100 | $45.04 |
| **answer engine optimization** | **2 400** | $30.77 |
| ai search optimization | 1 300 | $60.62 |
| geo optimization | 1 000 | $29.58 |
| chatgpt seo | 390 | $24.85 (low comp) |
| generative engine optimization | **0** | — |

### Pièges 0-volume identifiés (à NE PAS cibler)
`seo expert kenya` = 0 · `web design diani` = 0 · `web design mombasa` = 0 · `affordable web design kenya` = 0 · `freelance web developer kenya` = 0 · `local seo kenya/nairobi` = 0 · `generative engine optimization` = 0.

## 4. Phase 4 — On-page (FAIT)

### 4a. Landing (builtonresults.co.ke/)
- **H1** : `BUILT ON RESULTS.` → **`SEO Services in Kenya, Built on Results.`** (fusion mot-clé + marque, « Results. » gardé en surlignage coral).
- **Title** : `SEO Services in Kenya | Web Development | BuiltOnResults`
- **Meta** : mène par le mot-clé + « based in Kenya, delivered remotely worldwide » + CTA audit.
- **H2 services** : `Your SEO & Web Development Consultant in Kenya.` (singulier).
- **Schema** `ProfessionalService` : `serviceType` mène par « SEO Services » ; `areaServed: [Kenya, Worldwide]`.
- **Voix** : « We'll » → « I'll » (solo). Toutes les mentions « for the Kenyan market » associées à « and clients worldwide ».

### 4b. Cluster d'articles (4 — 1 article = 1 pilier de service)
| Article | Pilier | Mot-clé | Ce qui a changé |
|---|---|---|---|
| why-standard-seo-fails-kenyan-market | SEO services | `SEO in Kenya` | gardé ; lien interne mot-clé → landing |
| mpesa-mobile-first-speed | Web development | `M-Pesa integration` | **re-ciblé** (title/H1/meta/schema/keywords/contenu) depuis « online payments » (10/mo) |
| search-engines-to-ai-engines | GEO / AI (international) | `answer engine optimization` | **re-ciblé** depuis « generative engine optimization » (0/mo) ; dé-limité du Kenya |
| scaling-chef-angela-kenya | Preuve / case study | `Kenya SEO case study` | aligné (title/H1) ; reste la preuve sociale |

**Honnêteté** : l'article M-Pesa démontre l'expertise technique (Daraja API, STK push) SANS prétendre un historique de projets M-Pesa qu'OG-Elson n'a pas encore. Les chiffres du case study Chef Angela (#1 « private chef Diani », +$350/mo) n'ont pas été touchés — preuve réelle.

### 4c. Bugs corrigés (découverts pendant l'optimisation)
- **CTA « SEO Audit » cassé (404) sur les 4 articles** : pointaient vers `/seo-audit` (inexistant) → corrigé en `/audit`. C'était le call-to-action principal du blog, mort en prod.
- Schémas d'URL mixtes (`/flyer/` header/footer vs URLs propres corps) → uniformisés en URLs propres prod.

### 4d. Maillage interne
Chaque article linke désormais vers la landing avec une **ancre riche en mot-clé** (« SEO services in Kenya », « web development in Kenya », « SEO and answer engine optimization ») → aide la landing à ranker. Cartes « Recent Insights » de la landing + index `/insights/` mis à jour avec les nouveaux titres.

## 5. Ce qui N'EST PAS encore fait

- **Phase 1 — Tracking/baseline** : GSC non configuré, pas d'analytics (Plausible/GA4), pas de Google Business Profile.
- **Phase 2 — Indexation** : sitemap non soumis, aucun « request indexing » (volontaire — on optimise d'abord).
- **Phase 5 — Contenu** : 4 articles ok pour démarrer ; pas de nouveaux articles planifiés.
- **Phase 6 — Backlinks** : DR probablement 0. Aucun backlink construit. Priorité future : GBP + marketplaces freelance (Malt, Toptal, Upwork).
- **Phase 7 — GEO/LLM** : l'article AEO est un début ; pas de stratégie GEO complète.

## 6. Prochaines étapes (Étape 2 — fondations + indexation)

1. Vérifier `sitemap.xml` (inclut landing + 4 articles ?) + `robots.txt`.
2. **GSC** : vérifier la propriété (DNS), soumettre le sitemap, **request indexing** (Google crawle enfin la version optimisée).
3. **Google Business Profile** (SEO local Kenya).
4. Analytics baseline (Plausible auto-hébergé ou GA4).
> ⚠️ Gros de GSC/GBP = action d'OG-Elson (comptes). Claude prépare/vérifie le technique (sitemap, robots, checklist).

## 7. Résultat attendu

La landing + les 4 articles forment un **cluster cohérent** : 3 pièces Kenya (SEO / dev / preuve) + 1 pièce internationale (AEO). Quand l'indexation sera déclenchée, Google verra directement la version optimisée. Ranking réaliste : semaines-mois selon la concurrence (faible au Kenya = jouable même à DR 0).

---
*Références : [[seo_expert]] · [[copywriter_seo]] · memory `builtonresults-positioning-copy` · `seo-premium-dataforseo-wiring`. Outil DataForSEO = `search_api.py` (fonctions `dataforseo_volumes`/`dataforseo_ranked`).*
