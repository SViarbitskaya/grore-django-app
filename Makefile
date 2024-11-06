include .env
export

# Je pourrais intégrer docker dans les commandes make ... par le fait de prefixer ${EXEC_CMD} avant toutes les opérations 
ifeq (`echo $(ENVIRONMENT) | tr A-Z a-z`,"docker")
	EXEC_CMD := docker-compose exec -ti django
# Actually if the environment is nix, we will call make from nix
# else ifeq (`echo $(ENVIRONMENT) | tr A-Z a-z`,"nix")
# 	EXEC_CMD := nix-shell default.nix --command 
else
	EXEC_CMD :=
endif

init:
	$(EXEC_CMD) mkdir -p ${APP_WEB_ROOT}
	$(EXEC_CMD) mkdir -p ${DJANGO_MEDIA_ROOT}
	$(EXEC_CMD) mkdir -p ${DJANGO_STATIC_ROOT}
	$(EXEC_CMD) touch ./grore/settings_local.py
	$(EXEC_CMD) python -m venv ${APP_CACHE_ROOT}/.venv
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/pip install -r requirements.txt

init-admin-user:
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/python manage.py createsuperuser --username ${DJANGO_ADMIN_USER} --email ${DJANGO_ADMIN_EMAIL} --noinput 

load-fixtures:
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/python manage.py flush --no-input
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/python manage.py migrate
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/python manage.py loaddata scripts/data/classeur.json 
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/python manage.py loaddata scripts/data/page_fixtures.json 
	make init-admin-user

up:
	make init
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/pip install -r requirements.txt
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/python manage.py makemigrations --noinput
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/python manage.py migrate --noinput
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/python manage.py collectstatic --noinput

git-up:
	$(EXEC_CMD) git pull
	make up

restart: 
	make init
	$(EXEC_CMD) sudo /usr/bin/systemctl restart grore

runserver:
	make init
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/python manage.py runserver

nginxconf:
	make init
	envsubst < ./scripts/production/grore-nginx.conf.template > ./scripts/production/output/${APP_WEB_HOST}.conf

service:
	make init
	envsubst < ./scripts/production/grore.service.template > ./scripts/production/output/${APP_WEB_HOST}.service

production-prepare:
	make service
	make nginxconf

production-install:
	sudo mkdir -p ${DJANGO_MEDIA_ROOT}
	sudo mkdir -p ${DJANGO_STATIC_ROOT}
	sudo chown -R ${APP_DJANGO_USER_USER}:${APP_DJANGO_USER_GROUP} ${DJANGO_MEDIA_ROOT} ${DJANGO_STATIC_ROOT}
	sudo chmod -R 0775 ${DJANGO_MEDIA_ROOT} ${DJANGO_STATIC_ROOT}
	sudo chmod -R +s ${DJANGO_MEDIA_ROOT} ${DJANGO_STATIC_ROOT}
	sudo cp ${APP_DJANGO_ROOT}/scripts/production/output/${APP_WEB_HOST}.service /etc/systemd/system/${APP_WEB_HOST}.service
	sudo systemctl daemon-reload
	sudo systemctl enable --now ${APP_WEB_HOST}.service
	sudo nginx -t
	sudo cp ${APP_DJANGO_ROOT}/scripts/production/output/${APP_WEB_HOST}.conf /etc/nginx/sites-available/${APP_WEB_HOST}.conf
	sudo ln -s /etc/nginx/sites-available/${APP_WEB_HOST}.conf /etc/nginx/sites-enabled/${APP_WEB_HOST}.conf
	sudo nginx -t
	sudo systemctl restart nginx
	certbot --nginx -d ${APP_WEB_HOST} -d www.${APP_WEB_HOST}
	sudo systemctl restart grore nginx

default-pages:
	make up
	$(EXEC_CMD) ${APP_CACHE_ROOT}/.venv/bin/python manage.py loaddata scripts/data/page_fixtures.json

test-uploaded-images:
	echo "DOESN'T WORK"
	make init
	$(EXEC_CMD) PYTHONPATH="$PYTONPATH:`pwd`/images/";${APP_CACHE_ROOT}/.venv/bin/python scripts/tests/test_uploaded_images.py
	echo "DOESN'T WORK"

docker-compose-up:
	docker-compose up -d 

sys-install-nix-profile:
	mkdir -p ~/.config/nix
	! test -s ~/.config/nix/nix.conf && echo "experimental-features = nix-command flakes" > ~/.config/nix/nix.conf

sys-install-nix:
	echo "Install Nix on this local machine"
	sh <(curl -L https://nixos.org/nix/install) --daemon
	make sys-install-nix-profile

sys-install-nix-mac:
	echo "Install Nix on this local machine mode "
	sh <(curl -L https://nixos.org/nix/install)
	make sys-install-nix-profil

