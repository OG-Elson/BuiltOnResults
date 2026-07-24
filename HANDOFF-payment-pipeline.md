# HANDOFF — Payment / Conversion Pipeline (BuiltOnResults SEO tool)

> **À lire en début de session.** Rapport de passation rédigé le 2026-07-11 pour reprendre le travail sur le pipeline de paiement de l'outil d'audit SEO. Communication utilisateur = **français**. Persona = Senior Full-Stack Dev, solo freelance (voix « I », pas « we »).

---

## 1. Contexte & décision figée

L'outil d'audit SEO (`/home/deploy/builtonresults/seo-audit.html`, servi live sur http://46.224.49.147/flyer/seo-audit.html) génère des leads mais **le CTA payant est encore un `mailto`** → on perd les prospects. Objectif : brancher un **vrai encaissement + un pipeline optimisé conversion**, pour l'offre **audit à $15**.

**Réponses de l'utilisateur (contraintes qui verrouillent le choix) :**
- Compte bancaire : **seulement M-Pesa + 2 banques belges** — PAS de compte bancaire kényan.
- Statut : **pas encore formalisé / il débute** (pas de société).
- Périmètre pour l'instant : **uniquement l'audit $15** (petit ticket). Pas les projets freelance / pas de facturation lourde pour l'instant.
- Budget serré (recharge API min 50 €, ne pas gaspiller).
- Revolut voulu mais **KYC bloqué** → à ne PAS prioriser ; **Wise = remplaçant** plus tard.

**Conséquence :** toutes les passerelles lourdes (Stripe, Flutterwave/Paystack, M-Pesa Paybill/Till) sont **écartées** — elles exigent une entité ou un compte kényan. On part **zéro formalité, zéro code lourd, en ligne aujourd'hui**.

---

## 2. Ce qui est PLANIFIÉ MAINTENANT (le plan validé sur le principe)

### Phase 1 — lancer tout de suite, valider la demande
**Locaux 🇰🇪 — M-Pesa « Send Money » (perso)**
- Pas de Paybill/Till (exige une entreprise) → on affiche le **numéro M-Pesa perso** en « Send Money ».
- Checkout : *« Payer KES 2 000 par M-Pesa au +254 XX — puis envoie la capture sur WhatsApp »* → confirmation manuelle → livraison de l'audit.

**Étrangers 🌍 — PayPal.me d'abord, Gumroad ensuite**
- **Option A (retenue pour démarrer) : PayPal.me** (`paypal.me/<pseudo>/15`, cocher Goods & Services). 0 setup, il a déjà PayPal.
- **Option B (évolution) : Gumroad ou Lemon Squeezy** (merchant of record — encaisse la carte, gère la TVA, reverse sur PayPal/banque belge SANS société ; idéal pour un livrable digital comme un audit). À basculer après 2-3 ventes.
- Stripe / Wise / Revolut = plus tard, quand il formalise.

### Le livrable technique à coder (l'étape concrète suivante)
Remplacer le `mailto` dans `seo-audit.html` par un **bloc checkout à 2 chemins** :
```
Get your full audit — $15
  🇰🇪 In Kenya?  → Pay by M-Pesa : Send KES 2 000 to +254 XX, confirm on WhatsApp [btn]
  🌍 International? → [ Pay $15 with PayPal ] (lien paypal.me)
  You'll get your audit within 48h.
```
+ après paiement : **lien Calendly** (gratuit) pour l'appel + capture **URL du site + email** pour livrer.
- Bilingue EN/FR (l'outil a déjà un système i18n — respecter le pattern existant, NE PAS toucher à la logique calcul JS / DataForSEO / cache / i18n core).
- Mobile-first, esthétique éditoriale cohérente avec le reste (voir style existant du fichier).

---

## 3. CE QUI BLOQUE / À DEMANDER À L'UTILISATEUR AVANT DE CODER

Il manque **4 infos** (aucune sensible) pour brancher le bloc — les demander en début de session :
1. **Numéro M-Pesa** à afficher (ou placeholder si « plus tard »).
2. **Lien PayPal.me** (ou email PayPal pour générer le bouton).
3. **Numéro WhatsApp** (confirmation locale).
4. **Prix** confirmé : proposé **$15 / ~KES 2 000** — + veut-il **Calendly** oui/non (j'ajoute le champ lien).

→ Dès qu'il répond : coder le bloc checkout, montrer une **preview** (`seo-audit-preview.html` ou équivalent) AVANT de passer live. Ne pas déployer sans son « go » explicite (il n'a pas encore déployé de toute façon).

---

## 4. Garde-fous (règles encore actives)

- **Sécurité :** zéro credential/secret dans le code ou le channel. Ne PAS toucher à `~/.hermes/.env` ni aux configs nginx prod.
- **Ne PAS modifier** la logique calcul JS / DataForSEO / cache / i18n de l'outil (uniquement le bloc CTA/checkout).
- Voix **« I »** (solo, pas agence). Pas de framing « internet lent au Kenya » (le Kenya a un bon réseau).
- Commits atomiques, messages EN, **jamais** de signature « Generated with Claude ».
- Backend daemon `search_api.py` tourne sur `127.0.0.1:8083` derrière nginx `/flyer/api/search` — ne pas le tuer avec `pkill -f` (ça a déjà tué le shell : self-match). Relancer via `run_in_background` si besoin.

---

## 5. Fichiers clés

| Fichier | Rôle |
|---|---|
| `/home/deploy/builtonresults/seo-audit.html` | Outil live — c'est ici qu'on remplace le `mailto` par le bloc checkout |
| `/home/deploy/builtonresults/search_api.py` | Backend DataForSEO (ne pas toucher pour cette tâche) |
| `/home/deploy/builtonresults/test_seo_tool.py` | Suite de tests (MOCK=1 pour 0 coût API) |
| http://46.224.49.147/flyer/ | Base servie (preview + live) |

---

## 6. Tâches différées (décision de l'utilisateur, PAS pour maintenant)

- Valider les valeurs AOV/conversion par secteur dans l'outil.
- Reformuler la claim « #1 » dans les articles + landing (seul l'outil est corrigé).
- Déploiement Vercel (Option A : porter le backend en serverless).
- Petit ménage vault (maj `overview.md`, archiver `test_workflow_client.py`).
- Passer PayPal.me → Gumroad/Lemon Squeezy ; ouvrir **Wise** en remplacement de Revolut.

---

**Prochain pas immédiat en début de session :** saluer, pointer vers ce rapport, demander les **4 infos** du §3, puis coder le bloc checkout (preview avant live).
