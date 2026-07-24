# Audit de l'état réel — BuiltOnResults ⊕ Freelance (2026-07-20)

> Réalisé par Claude Code (session serveur, accès direct : fichiers, code, base Umami).
> Question centrale : **ce projet peut-il produire son premier contrat payé avant le 30/09/2026 ?**
> ⚠️ **Cadrage indispensable : le site est live depuis ~4 jours seulement** (domaine + Umami mis en place le 2026-07-16). Toute lecture des chiffres de trafic/conversion doit intégrer ça — on est au **jour 4**, pas au mois 4.

---

## 1. État de vérité — ce qui existe vraiment

**Actif en ligne (vérifié par requêtes HTTP le 2026-07-20, tous 200) :**
| Élément | URL | Statut |
|---|---|---|
| Site principal + SSL | `builtonresults.co.ke/` | ✅ 200, live |
| Outil d'audit SEO (gratuit) | `/audit` | ✅ 200, fonctionnel (front `seo-audit.html` + daemon `search_api.py` sur 127.0.0.1:8083) |
| Page audit payant | `/audits` | ✅ 200 |
| Consultation | `/consultation` | ✅ 200 |
| Blog | `/insights/` + **4 articles** | ✅ 200 (mpesa-mobile-first-speed, scaling-chef-angela-kenya, search-engines-to-ai-engines, why-standard-seo-fails-kenyan-market) |
| Showcase secteur | `/showcase/cleaning-mombasa` | ✅ 200 (finalisé ce jour) |
| Analytics | `analytics.builtonresults.co.ke` | ✅ 200, Umami opérationnel (2 sites enregistrés) |
| SEO technique | `/sitemap.xml`, `/robots.txt` | ✅ 200 |

**Outils réellement fonctionnels :** audit SEO (crawl + scorecard + concurrents SERP + estimation revenus, DataForSEO câblé — solde ~$0.06), pipeline paiement (Gumroad/PayPal/M-Pesa magic-link), moteur de prospection (`prospect_engine.py`), Umami instrumenté (events funnel).

**Prospects :** `prospects_cote_mombasa.csv` = **25 contacts qualifiés** (secteurs legal, cleaning… position SERP 11-30 + 3 problèmes on-page réels par crawl + coordonnées).

**Handles sociaux :** `DONNÉE MANQUANTE` — non vérifiable depuis le serveur (Instagram/Facebook/LinkedIn : statut de réservation inconnu). À confirmer manuellement.

**GSC :** vérifié ce mois selon les notes de session (sitemap soumis, ~7 URLs indexées, #2 sur le brand en <24h) — mais `DONNÉE MANQUANTE` pour une re-vérification live aujourd'hui (pas d'accès GSC depuis le serveur).

**Écart documentation vs réalité :** le handoff `handoff.md` (2026-06-24) affirme « aucun domaine ni handle sécurisé / Phase 0 ». **C'est faux** : site complet en ligne, outil + analytics opérationnels, 4 articles, showcase, 25 prospects. Le handoff est périmé (mise à jour proposée en fin de doc).

---

## 2. Offre et positionnement

- **Titre** (source `index.html`) : « SEO Services in Kenya | Web Development | BuiltOnResults ». **H1** : « SEO Services in Kenya, Built on Results. »
- **Positionnement** : **freelance solo** assumé (« Consultant » au singulier, voix « I »), **« Based in Kenya 🇰🇪 · Remote worldwide »** → Kenya-primary **mais** international. Cohérent sur toute la landing.
- **Services affichés** : classement Google (SEO), développement web, automation workflow. Message d'accroche : « I get you ranking on Google and converting, plus web development and automation ».
- **Prix / point d'entrée** :
  - **Audit gratuit** (`/audit`) = lead magnet, CTA présent sur la landing (`href="/audit"` ×3).
  - **Audit payant $15** = produit d'entrée.
  - **Consultation** = CTA de prise de contact.
  - **Offre cleaning (nouvelle, outbound)** : 10 000 KES, **pay-on-milestone** (site livré 3k → SEO+GBP 2k → top 20 : 2k → page 1 : 3k), 3 clients founding, inversion du risque.
- **Clarté (<10 s)** : ✅ globalement oui — un visiteur comprend « SEO + dev web, solo, Kenya + monde ». Le point faible n'est pas la clarté, c'est la **preuve** (section 4).

---

## 3. Acquisition et funnel

- **Canaux actifs aujourd'hui : quasi aucun.** Le site est jeune (4 j), **aucune campagne d'acquisition n'a encore été lancée**. Pas de pub, présence sociale non confirmée, organique inexistant (trop récent).
- **Outbound** : l'infrastructure est prête (moteur de prospection + **25 prospects qualifiés**), et l'**outreach cleaning (4 prospects) est prêt à envoyer** (`outreach/cleaning_send_links.md`, liens wa.me + A/B) — **mais pas encore envoyé au moment de l'audit**. → La liste existe et est qualifiée, **exploitation = 0 pour l'instant**.
- **Parcours visiteur** : audit gratuit → audit $15 / consultation. Funnel instrumenté (events Umami). **Pas d'email-gate** (bon point : la valeur est montrée avant toute capture).
- **Rupture principale** : il n'y a pas de « rupture de conversion » constatable — il n'y a **pas encore de trafic** pour en juger. La rupture est **en amont** : rien n'amène de visiteurs qualifiés.

---

## 4. Preuves et crédibilité

- **Portfolio / case studies** : un article « scaling-chef-angela-kenya » existe, et **Chef Angela est une vraie réalisation livrée** (`chefangela.co.ke` en ligne). Mais ce n'est pas encore une **case study à métriques** (chiffres avant/après vérifiables).
- **Tradehub** (prévu) : `DONNÉE MANQUANTE` — non trouvé publié sur le site.
- **Showcase cleaning** : c'est un **template de démo**, pas un résultat client réel (et l'outreach le présente honnêtement comme « an example »).
- **Témoignages / avis** : `DONNÉE MANQUANTE` — aucun trouvé.
- **Un prospect inconnu a-t-il une raison de faire confiance ? Franchement : faible aujourd'hui.** Une vraie réalisation (Angela) mais **aucune preuve chiffrée/témoignage public**. L'argument de vente outbound (« I took a Diani business from invisible to #1 on Google ») repose sur Angela → il **doit être matérialisé** par une case study chiffrée pour convertir des inconnus.

---

## 5. Mesure — données Umami (source : base MySQL `umami`, site `builtonresults.co.ke`)

⚠️ **Fenêtre de données = 2026-07-17 → 2026-07-20 (~4 jours).** Umami créé le 2026-07-16.

- **Trafic BuiltOnResults (tout l'historique)** : **6 pages vues, 6 sessions**, **100 % sur `/`**, **100 % en direct/sans referrer**. Pays : US 3, FR 2, CN 1, ? 1 → profil cohérent avec des **crawlers/bots + visites de dev**, pas une audience marché.
- **Events funnel personnalisés** (`paid_cta_click`, `free_lead`, `checkout_channel`, `paid_success`…) : **0**.
- **Leads (`leads.jsonl`)** : 9 entrées — mais **8 = l'email d'OG-Elson lui-même** (14/07) + **1 = `@test.com`** → **0 lead réel** (ce sont des tests de dev).
- **Audits (`audits.jsonl`)** : 2 — les deux sur `chefangela.co.ke`, gratuits, 11-14/07 → **tests de dev, 0 audit client réel**. `pending_payments` : 3 = flux de test.

**Lecture (avec le cadrage « jour 4 ») :** trafic réel ≈ 0, leads réels = 0, clients réels = 0 — **et c'est normal à ce stade.** Il est **trop tôt** pour que ces chiffres disent quoi que ce soit sur la conversion. Le diagnostic n'est donc **pas** « ça ne convertit pas » mais **« l'acquisition n'a pas encore commencé »**. Conformément à la consigne : trafic insuffisant ⇒ on ne conclut rien sur la conversion.

---

## 6. Verdict

**Peut-il produire un premier contrat payé avant le 30/09/2026 ? → OUI, sous conditions.**
C'est réaliste, **pas** par complaisance, parce que : (a) l'**actif est construit et fonctionnel** (site + outil + showcase), (b) une **liste de 25 prospects qualifiés** existe, (c) l'**outbound cleaning est prêt à partir aujourd'hui**, (d) l'offre milestone **casse le risque acheteur**. Le chemin vers le 1ᵉʳ euro passe par l'**outbound**, pas par l'attente d'organique — et il est à portée immédiate.

**Goulot d'étranglement principal (un seul, le plus limitant) : l'ACQUISITION — précisément, la mettre réellement en route à volume.** Tout l'amont (actif, offre, outil) est prêt ; rien en aval ne compte tant qu'il n'y a pas de conversations. La preuve/crédibilité (section 4) est le **second** frein, qui pèsera sur le taux de réponse.

**3 actions à plus fort impact/effort (6 semaines) :**
1. **Lancer l'outbound MAINTENANT et à volume** — envoyer les 4 messages cleaning aujourd'hui, puis travailler toute la liste (25) et l'élargir. C'est la **seule** action qui produit un contrat d'ici le 30/09.
2. **Publier UNE case study chiffrée (Chef Angela)** — « d'invisible à #1 sur Google » avec vrais chiffres GSC → donne à un inconnu une raison vérifiable de faire confiance (relève directement le taux de réponse/closing outbound).
3. **Fluidifier le chemin réponse → closing** — proposition milestone prête + prise de RDV sans friction (WhatsApp/Calendly). Le hook audit gratuit est déjà là.

**Critère de pivot mesurable (chiffres concrets, à surveiller) :**
- **Indicateur avancé (hebdo)** : nombre de prospects **réellement contactés** + **taux de réponse**. Si après **30 messages envoyés** le taux de réponse est **< 5 %** → corriger message/preuve **avant** de scaler.
- **Jalon 2026-08-31 (6 sem.)** : si après **≥ 40 prospects contactés** il y a **< 3 vraies conversations** (prospect qui engage au-delà du 1ᵉʳ message) → le problème est l'offre/le message/le marché → itérer l'offre.
- **Jalon 2026-09-30 (décision de pivot)** : **0 KES encaissé** (même pas un palier 1 à 3 000 KES) malgré **≥ 40 contactés et ≥ 3 conversations** ⇒ **MVP non validé → décision de pivot** (canal, secteur ou offre). Seuil clair : **0 € au 30/09 = pivot.**

**Délai réaliste jusqu'au premier euro :** avec l'outbound démarré aujourd'hui et des PME cleaning joignables sur WhatsApp, **2 à 5 semaines** pour un **premier palier encaissé (3 000 KES ≈ 23 €)** est réaliste **si** l'outbound tourne à volume et qu'un prospect convertit. La structure milestone fait arriver le 1ᵉʳ euro **avant** le contrat complet — c'est un atout pour la trajectoire Q4.

---

## Ce que je n'ai pas pu vérifier
- **Handles sociaux** (Instagram/Facebook/LinkedIn) : réservés ou non → à confirmer manuellement.
- **État GSC live** (URLs indexées, position brand) aujourd'hui : rapporté ce mois, non re-vérifié depuis le serveur.
- **Contacts déjà pris hors canal tracké** : impossible à confirmer (les 25 prospects semblent tous non contactés).
- **Taux de conversion réels** : impossibles à établir — trafic insuffisant (site à 4 jours).
- **Contenu exact des `pending_payments`** (test vs réel) : présumés tests, non ouverts en détail.

## Mise à jour proposée du handoff (l'actuel, 2026-06-24, est périmé)
> **Statut : Phase 1 — actif construit, lancement outbound imminent** (et non « Phase 0 / rien de sécurisé »).
> - Domaine `builtonresults.co.ke` **live + SSL** ; sous-domaine analytics Umami opérationnel.
> - Site : landing + `/audit` (outil SEO fonctionnel) + `/audits` + `/consultation` + `/insights` (4 articles) + `/showcase/cleaning-mombasa`.
> - Positionnement : freelance solo, « Based in Kenya · Remote worldwide », SEO + dev web + automation ; produit d'entrée audit $15 + audit gratuit ; offre cleaning milestone 10k KES.
> - Prospection : moteur + **25 prospects qualifiés** (CSV), outreach cleaning **prêt** (non encore envoyé).
> - **Prochaine étape unique : envoyer l'outbound à volume + publier la case study Angela.**
> - Trafic/leads réels = 0 **au jour 4** (acquisition pas encore lancée) → ce n'est pas un problème de conversion.
