# Commandes Makefile

Il n'y a pas de variante `-nix` des commandes `make` : la branche `ENVIRONMENT=nix` du Makefile est du code mort (commenté). Pour travailler sous Nix, entrez dans le shell défini par `default.nix` vous-même, puis lancez les commandes normales depuis cet environnement. Seul `ENVIRONMENT=docker` change réellement le comportement du Makefile (les commandes passent alors par `docker-compose exec`).

Voici les commandes principales

| command make | explication |
| --- | --- |
| `make up` | Installe les dépendances, `makemigrations`, `migrate`, `collectstatic` |
| `make default-pages` | `make up` puis chargement de `scripts/data/page_fixtures.json` |
| `make runserver` | Tourne un serveur de développement (dev sans avoir mis à jour) |
| `make production-prepare` | Crée les fichiers de configuration dans `./scripts/production/output/` (nginx et service systemd) |
| `make production-install` | Fait toutes les opérations sur NGINX et SYSTEMD en tant que SUDO |
| `make restart` | Redémarre le service systemd `grore` |

Voici les commandes intermédiaires

| command make | explication |
| --- | --- |
| `make init` | Etablit l'environnement de base Python (crée les dossiers, le venv, installe les dépendances) |
| `make init-admin-user` | Crée le superuser Django depuis les variables `DJANGO_ADMIN_*` de `.env`, sans interaction |
| `make load-fixtures` | Vide la base, migre, charge `media_fixture.json` + `scripts/data/page_fixtures.json`, génère les embeddings, crée le superuser |
| `make git-up` | Réservé au déploiement (pas pour le dev local) : `git fetch` + `git reset --hard @{u}` puis `make up` |
| `make nginxconf` | Crée le fichier de config `scripts/production/output/${APP_WEB_HOST}.conf` |
| `make service` | Crée le fichier de config `scripts/production/output/${APP_WEB_HOST}.service` |
| `make sys-install-nix` ou `make sys-install-nix-mac` | Installe Nix sur votre propre ordinateur linux (y compris wsl) ou mac |

Voici les commandes Docker Compose

| command make | explication |
| --- | --- |
| `make docker-compose-up` | `docker-compose up -d` |
| `make docker-rebuild-recompose-up` | Supprime le conteneur et l'image `django`, puis relance `docker compose up -d` |

Commande cassée (voir le Makefile, marquée `"DOESN'T WORK"`) :

| command make | explication |
| --- | --- |
| `make test-uploaded-images` | Actuellement non fonctionnelle |
