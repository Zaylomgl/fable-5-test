# fable-5-test

## Quoi
Dépôt d'essai qui contient deux projets dans deux PR : une boîte à outils perso de 42 scripts Python, et StackAlert (alertes CVE filtrées par logiciels utilisés).

## Pour qui / pourquoi
Boîte à outils : usage personnel. StackAlert : petites équipes IT et MSP (idée « CVE Radar »).

## Périmètre V1 (code existant au 2026-11-18, PR ouvertes comprises)
- PR boîte à outils : 42 outils en ligne de commande, sans dépendance
- PR StackAlert : ingestion NVD/KEV/EPSS, moteur de correspondance, digest e-mail/Slack, page d'attente en 5 langues

## Hors périmètre
- Encaissement (StackAlert est en phase de validation)

## Stack / outils
Python standard ; Netlify pour la page d'attente de StackAlert.

## Où ça vit
À la racine du dépôt, sur la branche `main` : `PROJECT.md`, `DECISIONS.md`, `PROGRESS.md`, `CLAUDE.md`.
