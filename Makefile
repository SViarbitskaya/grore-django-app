include .env
export

USE_DOCKER := 0
# Je pourrais intégrer docker dans les commandes make ... par le fait de prefixer ${EXEC_CMD} avant toutes les opérations 
ifeq ($(USE_DOCKER),1)
	EXEC_CMD := docker-compose -f ./scripts/docker/docker-compose.yml exec -ti web
else
	EXEC_CMD :=
endif

init:
	$(EXEC_CMD) mkdir -p ${APP_WEB_ROOT}
	$(EXEC_CMD) mkdir -p ${DJANGO_MEDIA_ROOT}
	$(EXEC_CMD) mkdir -p ${DJANGO_STATIC_ROOT}
	$(EXEC_CMD) touch ./grore/settings_local.py
	$(EXEC_CMD) python -m venv venv  # Not sure about this in docker
	$(EXEC_CMD) ${APP_DJANGO_ROOT}/venv/bin/pip install -r requirements

init-nix:
	nix-shell default.nix --command "make init"

load-fixtures:
	$(EXEC_CMD) ${APP_DJANGO_ROOT}/venv/bin/python manage.py flush --no-input
	$(EXEC_CMD) ${APP_DJANGO_ROOT}/venv/bin/python manage.py migrate
	$(EXEC_CMD) ${APP_DJANGO_ROOT}/venv/bin/python manage.py loaddata scripts/data/classeur.json 

load-fixtures-nix:
	nix-shell default.nix --command "make load-fixtures"

up:
	make init
	$(EXEC_CMD) ${APP_DJANGO_ROOT}/venv/bin/pip install -r requirements.txt
	$(EXEC_CMD) ${APP_DJANGO_ROOT}/venv/bin/python manage.py makemigrations --noinput
	$(EXEC_CMD) ${APP_DJANGO_ROOT}/venv/bin/python manage.py migrate --noinput
	$(EXEC_CMD) ${APP_DJANGO_ROOT}/venv/bin/python manage.py collectstatic --noinput

up-nix:
	nix-shell default.nix --command "make up"

git-up:
	$(EXEC_CMD) git pull
	make up

git-up-nix:
	nix-shell default.nix --command "make git-up"

restart: 
	make init
	$(EXEC_CMD) sudo /usr/bin/systemctl restart grore

restart-nix: 
	nix-shell default.nix --command "make restart"

runserver:
	make init
	$(EXEC_CMD) ${APP_DJANGO_ROOT}/venv/bin/python manage.py runserver

runserver-nix:
	nix-shell default.nix --command "make runserver"

nginxconf:
	make init
	envsubst < ./scripts/production/grore-nginx.conf.template > ./scripts/production/output/${APP_WEB_HOST}.conf

nginxconf-nix:
	nix-shell default.nix --command "make nginxconf"

service:
	make init
	envsubst < ./scripts/production/grore.service.template > ./scripts/production/output/${APP_WEB_HOST}.service

service-nix:
	nix-shell default.nix --command "make service"

production-prepare:
	make service
	make nginxconf

production-prepare-nix:
	nix-shell default.nix --command "make production-prepare"

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

production-install-nix:
	nix-shell default.nix --command "make production-install"

default-pages:
	make up
	$(EXEC_CMD) ${APP_DJANGO_ROOT}/venv/bin/python manage.py loaddata scripts/data/page_fixtures.json

default-pages-nix:
	nix-shell default.nix --command "make default-pages"

test-uploaded-images:
	echo "DOESN'T WORK"
	make init
	$(EXEC_CMD) PYTHONPATH="$PYTONPATH:`pwd`/images/";${APP_DJANGO_ROOT}/venv/bin/python scripts/tests/test_uploaded_images.py
	echo "DOESN'T WORK"

test-uploaded-images-nix:
	nix-shell default.nix --command "make test-uploaded-images"

docker-compose-up:
	make init
	cd ./scripts/docker
	docker-compose up -d 
	cd ../..

docker-compose-up-nix:
	nix-shell default.nix --command "make docker-compose-up"

docker-nginx:
	make init
	echo "I don't know how to execute this file scripts/docker/nginx/Dockerfile"

docker-nginx-nix:
	nix-shell default.nix --command "make docker-nginx"

docker-postgres:
	make init
	echo "I don't know how to execute this file scripts/docker/Dockerfile"

docker-postgres-nix:
	nix-shell default.nix --command "make docker-postgres"


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

