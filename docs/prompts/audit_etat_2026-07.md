# Prompt — Audit de l'état réel BuiltOnResults ⊕ Freelance (juillet 2026)

> À transmettre à Cowork. Rapport attendu : `vault/projects/builtonresults/audit_etat_2026-07.md`.
> Rédigé par Claude Code le 2026-07-20 à la demande d'OG-Elson.

---

## Ton rôle

Tu établis **l'état de vérité** de ce projet, puis tu réponds à une question unique :
**ce projet peut-il produire son premier contrat payé avant le 30/09/2026 ?**

Ce n'est pas un audit de conformité, c'est un audit de faisabilité commerciale.

## Contexte à intégrer

- **BuiltOnResults ⊕ Freelance** est le stream le plus lourd du portefeuille : cible **700 €/mois
  au 31/12/2027**, soit **35 % de la North Star** (2000 € de MRR-LI).
- Premier revenu attendu dès le **Q4'26 : 100 €/mois**, sur un palier trimestriel total de 115 €.
  Autrement dit, **87 % du premier palier de la trajectoire repose sur ce projet**. S'il glisse,
  c'est la trajectoire entière qui rate sa première marche.
- Statut déclaré : « Phase 0 — lancement ». Prochaine étape déclarée : « domaines + portfolio +
  case study Angela ».
- **OG-Elson envisage un pivot** si le MVP n'est pas validé assez vite. Ton audit doit l'aider à
  définir un critère de pivot mesurable, pas à le rassurer.

## ⚠️ Point de départ obligatoire : la documentation est périmée

Le handoff `projects/builtonresults/handoff.md` date du **2026-06-24** et affirme « Aucun domaine
ni handle encore sécurisé ». **C'est faux.** Vérification faite le 2026-07-20 sur le serveur :

- `builtonresults.co.ke` est **en ligne avec SSL** (nginx + Certbot)
- `analytics.builtonresults.co.ke` sert une instance **Umami** opérationnelle
- Le site compte environ **7 pages** plus des articles SEO
- Un **outil d'audit SEO** existe (`seo-audit.html` + `search_api.py`)
- Une liste de prospects existe (`prospects_cote_mombasa.csv`)
- Des **templates de démo par secteur** sont en construction (`showcase/`)

**Ta première tâche est donc d'établir ce qui existe réellement**, pas de partir du handoff.
Traite tout document antérieur au 2026-07-01 comme non fiable jusqu'à vérification.

## Ce que tu dois produire

### 1. État de vérité — ce qui existe vraiment
- Inventaire de l'actif numérique : domaines détenus, sous-domaines actifs, pages en ligne,
  articles publiés, outils fonctionnels
- Pour chaque élément : **est-il réellement accessible et fonctionnel**, ou en chantier ?
- Handles sociaux : réservés ou non (Instagram, Facebook, LinkedIn)
- Écart entre ce que la documentation prétend et ce qui est constaté

### 2. Offre et positionnement
- Quels services sont effectivement proposés, avec quel niveau de détail public
- Positionnement affiché (freelance vs agence), langue, cible géographique
- Politique de prix : y a-t-il une grille, un point d'entrée, un mécanisme de devis ?
- Le visiteur comprend-il en moins de 10 secondes ce qui est vendu et à qui ?

### 3. Acquisition et funnel
- Canaux actifs et leur état réel
- La liste de prospects existante : combien de contacts, quelle qualification, a-t-elle été
  exploitée ?
- Le parcours complet du visiteur jusqu'à la prise de contact : où sont les ruptures ?
- Y a-t-il une offre d'appel gratuite ? Convertit-elle vers du payant ?

### 4. Preuves et crédibilité
- Portfolio : existe-t-il, est-il en ligne, que contient-il ?
- Case studies : Chef Angela et Tradehub sont prévus — quel est leur état réel ?
- Témoignages, avis, références vérifiables
- **Un prospect inconnu a-t-il une raison de faire confiance ?** Réponds franchement.

### 5. Mesure — utilise les données, pas les impressions
Umami est installé et instrumenté avec des events de funnel (`paid_cta_click`,
`checkout_channel`, `free_lead`, `consultation_submit`, `paid_success`, `brief_received`).

- Trafic réel sur les 30 derniers jours : volume, sources, pages d'entrée
- Events déclenchés : combien, lesquels, à quelle étape ça décroche
- Taux de conversion visiteur → lead → contact qualifié → devis
- **Si le trafic est proche de zéro, dis-le clairement** — ça change entièrement le diagnostic :
  ce n'est plus un problème de conversion mais d'acquisition

### 6. Verdict — la partie qui compte
- **Ce projet peut-il produire un premier contrat payé avant le 30/09/2026 ?** Oui / Non / Sous
  conditions — et lesquelles précisément.
- Le **goulot d'étranglement principal** : trafic ? offre ? preuve ? prix ? prospection ?
  Un seul, le plus limitant.
- Les **3 actions** à plus fort rapport impact/effort pour les 6 prochaines semaines
- **Un critère de pivot mesurable** : quel indicateur, à quelle date, en dessous de quel seuil
  OG-Elson devrait considérer que le MVP n'est pas validé. Propose un chiffre concret, pas un
  principe.
- Estimation réaliste du **délai jusqu'au premier euro**

## Format et livraison

- Fichier : `vault/projects/builtonresults/audit_etat_2026-07.md`
- Structure : les 6 sections ci-dessus, dans cet ordre
- Chaque constat doit citer sa source (URL testée, données Umami, fichier du dépôt)
- Si une donnée est introuvable, écris **`DONNÉE MANQUANTE`** — n'estime jamais un chiffre sans
  le signaler explicitement
- Termine par **« Ce que je n'ai pas pu vérifier »** et par une **mise à jour proposée du
  handoff**, puisque l'actuel est périmé

## Ce que tu ne dois pas faire

- Ne pas te fier au handoff ni à aucune documentation antérieure à juillet sans vérification
- Ne pas confondre « le site existe » et « le site convertit »
- Ne pas conclure à un problème de conversion si le trafic est insuffisant pour conclure quoi que
  ce soit
- Ne pas adoucir le verdict : ce projet porte 35 % de la North Star, une évaluation complaisante
  coûterait des mois
