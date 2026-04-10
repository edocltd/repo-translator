<!-- i18n-source: CONTRIBUTING.md -->
<!-- i18n-date: 2026-04-10 -->

# Contribuer à repo-translator

Merci de votre intérêt. Ce guide couvre le processus et les normes pour apporter des modifications.

## Types de contributions

- **Corrections de bugs** — Résoudre les problèmes de scan, validation ou ancres
- **Nouvelles vérifications** — Ajouter des vérifications détectant de vrais problèmes de traduction
- **Support linguistique** — Ajouter des glossaires, tester de nouvelles langues
- **Documentation** — Améliorer les explications, ajouter des exemples
- **Traductions** — Traduire la documentation du projet avec l'outil lui-même

## Démarrage

```bash
git clone https://github.com/edocltd/repo-translator.git
cd repo-translator
git checkout -b your-branch-name
```

Aucune dépendance externe requise pour les scripts principaux.

## Normes de code

- Python 3.10+ avec annotations de type modernes
- Fonctions avec docstrings
- Pas de code mort ni d'imports inutilisés
- Pas de chemins codés en dur — utiliser des objets `Path`
- Pas de fonctions placeholder ni de code commenté

## Messages de commit

Suivre les conventional commits : `type(scope): description`

Types : `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Licence

En contribuant, vous acceptez que vos contributions soient sous licence MIT.
