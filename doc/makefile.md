# Commandes Makefile

Toute commande `make` peut être post-fixé `-nix` pour exécuter la commande dans l'environnement nix spécifié par `scripts/default.nix`.

Voici les commandes principales

| command make | explication |
| --- | --- |
| `make up` / `make up-nix` | Met à jour et initialize l'environnement actuel  | 
| `make default-pages` / `make default-pages-nix` | Ajout des pages par défault  | 
| `make runserver` / `make runserver-nix` |  Tourne un serveur de développement (dev sans avoir mis à jour) | 
| `make production-prepare` / `make production-prepare-nix` | Crée les fichiers de configuration dans ./scripts/production/output/ (nginx et service systemd)  | 
| `make production-install` / `make production-install-nix` |  Fait toutes les opérations sur NGINX et SYSTEMD en tant que SUDO | 
| `make restart` / `make restart-nix`  | Met à jour et redémarre le serveur en production  | 

Voici les commandes intermédiaires

| command make | explication |
| --- | --- |
| `make init` / `make init-nix` | Etablit l'environnement de base Python (ne fait pas `source ./venv/bin/activate`)  | 
| `make nginxconf` / `make nginxconf-nix` |  Crée le fichier de config scripts/production/output/webser.nginx | 
| `make service` / `make service-nix` |  Crée le fichier de config scripts/production/output/grore.service | 
| `make sys-install-nix` ou `make sys-install-nix-mac` | Installe Nix sur votre propre ordinateur linux (y compris wsl) ou mac |

Voici les commandes en travaux

| command make | explication |
| --- | --- |
| `make docker-compose-up` / `make docker-compose-up-nix` |   | 
| `make docker-nginx` / `make docker-nginx-nix` |   | 
| `make docker-postgres` / `make docker-postgres-nix` |   | 
| `make test-uploaded-images` / `make test-uploaded-images-nix` |   | 