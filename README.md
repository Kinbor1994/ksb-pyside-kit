# ksb_pyside_kit

ksb_pyside_kit est un framework léger pour construire des applications de bureau avec PySide (Qt for Python), conçu pour suivre la structure et les conventions de Django. L'objectif est que tout développeur familier avec Django puisse reprendre ses habitudes (apps, models, forms, "views"/controllers, commandes de gestion) pour créer des applications desktop modulaires et maintenables.

## Objectifs

- Proposer une architecture proche de Django adaptée aux applications desktop.
- Fournir des composants UI réutilisables, des widgets bas niveau, un système de forms lié aux modèles et des controllers (équivalents des views).
- Faciliter le prototypage et la scalabilité d'applications desktop avec une expérience de développement similaire à Django.

## Concepts (mapping Django → ksb_pyside_kit)

- App Django → sous-package / module (ex. `authentication/`, `components/`)
- Models → `models/` (définition des données et métadonnées)
- Views → `controllers/` (logique applicative, actions)
- Forms → `forms/` et `core/base_form_field.py` (liaison UI ↔ modèle)
- Templates → `themes/` (styles et templates pour formulaires/composants)
- manage.py → scripts dans `cli/` (gestion d'apps, migrations, utilisateurs)
- Widgets/Components → `widgets/` et `components/` (éléments UI réutilisables)

## Fonctionnalités principales

- Architecture façon Django (apps, models, controllers, forms, CLI)
- Widgets Qt prêts à l'emploi (button, text_field, combobox, textarea, etc.)
- Composants UI composites (navbar, sidebar, dashboard, contentarea, table_view...)
- Thèmes par formulaire pour homogénéiser l'UI
- Exemple d'authentification (controllers + models + forms)
- CLI d'administration et outils de migration
- Exemples et tests pour démarrage rapide

## Installation (Poetry — Windows)

1. Cloner le dépôt et se placer dans le dossier du projet.
2. Installer les dépendances :
   - poetry install
3. Ajouter PySide6 si nécessaire :
   - poetry add PySide6
4. Lancer un exemple :
   - poetry run python examples\auth_example.py
   - ou : poetry run python -m ksb_pyside_kit.examples.auth_example

## Démarrage rapide pour un développeur Django

1. Créer une nouvelle "app" en tant que sous-package.
2. Définir vos modèles dans models/, vos formulaires dans forms/ et la logique dans controllers/.
3. Réutiliser les composants UI de `components/` et `widgets/` pour composer vos vues desktop.
4. Utiliser les scripts dans `cli/` pour gérer l'app et les utilisateurs comme avec manage.py.

## Structure du projet

- authentication/ — app d'authentification (controllers, modèles, forms)
- components/ — composants UI composites
- widgets/ — widgets Qt bas niveau
- forms/ — forms et model-form
- models/ — modèles de données et metadata
- controllers/ — logique applicative (équivalent des views)
- core/ — classes de base et utilitaires
- themes/ — styles / templates pour formulaires
- cli/ — commandes de gestion
- examples/ — démonstrations d'utilisation
- tests/ — tests unitaires

## Développement & tests

- Installer dépendances dev via poetry (ajouter pytest, black, flake8 si besoin) :
  - poetry install
- Lancer les tests :
  - poetry run pytest
- Formattage/lint : configurer black / flake8 / isort dans pyproject.toml

## Contribution

Projet open source — contributions bienvenues.

- Fork → branche feature/bugfix → PR avec description et tests.
- Respecter la structure Django-like du projet pour la cohérence.

## Licence

Projet open source.
