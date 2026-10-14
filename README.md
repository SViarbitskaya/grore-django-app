# GRORE

Production :  
[grore-images.com](https://www.grore-images.com)

Integration :  
[grore-images.demarchic.com](https://grore-images.demarchic.com)

Hébergé par [Hetzner](https://www.hetzner.com), serveur \#54912924 à Nuremberg, Allemagne

En bref, Grore utilise Nixpkgs (pas NixOS) pour gérer son environnement d'exécution, et peut résider sur n'importe quel serveur Linux à partir du moment où Nixpkgs est accessible. Cela permet un contrôle sur l'environnement d'exécution sans induire une charge trop importante en administration système.

## Table des matières

- [Présentation](#grore)
- [Quick start](#quick-start)
- [Documentation principale](#documentation-principale)
- [Documentation secondaire](#documentation-secondaire)
- [Changelog](#changelog)
- [Contact / Hébergement](#contact--hébergement)

## Quick start

Clonez le dépôt et lancez une instance de développement minimale.

Non-Nix (virtualenv):

```bash
git clone <repo-url>
cd grore-django-app
cp scripts/sample.env .env    # puis modifier .env — voir doc/configuration.md
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Nix (si vous utilisez Nix): consultez `doc/installation.md` pour la procédure complète.

## Documentation principale

| Section | Description | Lien |
|---|---|---|
| Configuration | Paramètres et variables d'environnement | [./doc/configuration.md](./doc/configuration.md) |
| Développement | Guide pour le développement local | [./doc/dev.md](./doc/dev.md) |
| Installation | Instructions d'installation | [./doc/installation.md](./doc/installation.md) |
| Intégration | Détails pour déploiement et intégration | [./doc/integration.md](./doc/integration.md) |
| Makefile | Rappels des commandes Make disponibles | [./doc/makefile.md](./doc/makefile.md) |

## Documentation secondaire

- [./doc/architecture.md](./doc/architecture.md) — Architecture du projet
- [./doc/continuous.md](./doc/continuous.md) — CI / intégration continue
- [./doc/docker.md](./doc/docker.md) — Utilisation via Docker
- [./doc/images.md](./doc/images.md) — Gestion des champs image et recherche sémantique

## Changelog

Voir `CHANGELOG.md` pour l'historique des versions.

## Contact / Hébergement

Production : [grore-images.com](https://www.grore-images.com)

Integration : [grore-images.demarchic.com](https://grore-images.demarchic.com)

Hébergé par [Hetzner](https://www.hetzner.com)

