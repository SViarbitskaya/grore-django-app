# Configuration

L'ensemble de la configuration se trouve dans le fichier .env. Pour créer ce fichier, 

`cp scripts/sample.env .env`

Il y a des exemples de fichier de configuration dans les dossier  ̀scripts/*.env`.

**Ne pas mettre aucune valeur entre guillements (") ni simple quotes (')**   
Le Makefile utilise ce fichier .env et a une habitude de les reprendre de manière littérale.

Voici les variables de configuration :

| Paramètre | Explication / Exemple|
| --- | --- | 
| APP_DJANGO_ROOT |  Le dossier depuis dans lequel on trouve `manage.py`  **démarre avec "/" et termine sans "/"**. ${PWD} est habituellement le dossier courant. |
|  |  ${PWD}  |
| APP_CACHE_ROOT |  Le dossier pour des fichiers volatiles  **démarre avec "/" et termine sans "/"**. ${PWD} est habituellement le dossier courant. |
|  |  ${APP_DJANGO_ROOT}/.cache  |
| APP_DJANGO_USER_GROUP |  Pour le service Systemd et pour Docker |
|  |  Django  |
| APP_DJANGO_USER_GID | GID known to Docker from `id -g` |
| | 1000 |
| APP_DJANGO_USER_UID | UID known to Docker from `id -u` |
| | 1000 |
| APP_DJANGO_USER_USER | Pour le service Systemd et pour Docker |
|  |  django  |
| APP_WEB_HOST | Partie externe après "://" et avant "/" peut être directement Django. Peut être le même que DJANGO_HOST. Utilisé par NGINX aussi. |
|  |  grore-images.com ou 127.0.0.1 ou localhost |
| APP_WEB_PORT | Le port visible à l'extérieur (identique que intérieur si absence proxy)  |
|  |  443 ou 80 ou 8000  |
| APP_WEB_PROTO | Partie externe http peut être directement Django  |
|  |  https ou http |
| APP_WEB_ROOT | Dossier pour la racine du proxy web sous lequel on trouve habituellement media et staticfiles **démarre avec "/" et termine sans "/"**  |
|  |  /var/www/html/grore ou ${APP_DJANGO_ROOT}/cache/www |
| DB_DATABASE | Le nom de la base de données (ou le fichier chemin absolu si SQLite3, mais attention, le dossier doit exister)  |
|  |  grore ou ${APP_DJANGO_ROOT}/cache/db.sqlite3 |
| DB_ENGINE |  Le type de base de données |
|  |  django.db.backends.postgresql (ou .sqlite3)  |
| DB_HOST |   |
|  |  localhost  |
| DB_PASSWORD |   |
|  |  CHANGE_ME  |
| DB_PORT |   |
|  |  5432  |
| DB_USER |   |
|  |  grore  |
| DEBUG |  Pour DJANGO |
|  |  false  |
| DJANGO_ALLOWED_HOSTS |  La partie après "://" et avant ":" et avant "/", pour avoir permission d'y accéder. Pas besoin d'indiquer le port. |
|  |  localhost, 127.0.0.1, grore-images.com, ${APP_WEB_HOST}  |
| DJANGO_HOST |  La partie après "://" et avant "/" où le serveur Django ou Gunicorn écoute principalement  |
|  |  localhost ou  ou ${APP_WEB_HOST}  |
| DJANGO_LANGUAGE_CODE | La langue (par défaut ?) du site  |
|  |  en ou fr  |
| DJANGO_MEDIA_ROOT |  Ce dossier est créé avec `make init-nix`. **démarre avec "/" et termine sans "/"** |
|  |  /var/www/html/grore/media  |
| DJANGO_MEDIA_URL | **ni "/" avant ni "/" après**  |
|  |  media  |
| DJANGO_PORT | pour gunicorn ou django  |
|  |  8000 ou ${APP_WEB_PORT} |
| DJANGO_PROTO | https ou http pour gunicorn ou django  |
|  |  http  |
| DJANGO_SETTINGS_MODULE | N'est guère utilisé actuellement en interne mais pris automatiquement par DJANGO |
|  |  grore.settings  |
| DJANGO_STATIC_ROOT | Ce dossier est créé avec `make init-nix`. **démarre avec "/" et termine sans "/"**. |
|  | ${APP_DJANGO_ROOT}/cache/www/staticfiles ou /var/www/html/grore/staticfiles  |
| DJANGO_STATIC_URL |  **ni "/" avant ni "/" après**  |
|  |  static  |
| ENVIRONEMENT |  Est-ce que nous utilisons le docker-compose ?  True ou False |
|  |  False  |
| NGINX_DOMAINS |  Configuration de proxy NGINX partie après "://" et avant premier / |
|  |  www.grore-images.com grore-images.com et éventuellement ${APP_WEB_HOST} / ${DJANGO_HOST} |
| NGINX_MAX_SIZE | Taille max des fichiers  |
|  |  500M  |
| SECRET_KEY |  Pour Django/ Gunicorn |
|  |  ./venv/bin/python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"  |
