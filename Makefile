include .env
export

ifeq ($(USE_DOCKER),1)
	EXEC_CMD := docker-compose -f ./scripts/docker/docker-compose.yml exec -ti web
else
	EXEC_CMD :=
endif

python:
	mkdir -p ${DJANGO_NGINX_ROOT}
	mkdir -p ${DJANGO_MEDIA_ROOT}
	mkdir -p ${DJANGO_STATIC_ROOT}
	python -m venv venv

python-nix:
	nix-shell scripts/default.nix --command "make python"

up:
	make python
	git pull
	touch ./grore/settings_local.py
	./venv/bin/pip install -r requirements.txt
	./venv/bin/python manage.py makemigrations --noinput
	./venv/bin/python manage.py migrate --noinput
	./venv/bin/python manage.py collectstatic --noinput

up-nix:
	nix-shell scripts/default.nix --command "make up"

restart: 
	make python
	sudo /usr/bin/systemctl restart grore

restart-nix: 
	nix-shell scripts/default.nix --command "make restart"

runserver:
	make python
	./venv/bin/python manage.py runserver

runserver-nix:
	nix-shell scripts/default.nix --command "make runserver"

nginxconf:
	make python
	envsubst < ./scripts/production/grore-nginx.conf.template > ./scripts/production/output/${WEB_DOMAIN}.conf

nginxconf-nix:
	nix-shell scripts/default.nix --command "make nginxconf"

service:
	make python
	envsubst < ./scripts/production/grore.service.template > ./scripts/production/output/grore.service

service-nix:
	nix-shell scripts/default.nix --command "make service"

production-prepare:
	make service
	make nginxconf

production-prepare-nix:
	nix-shell scripts/default.nix --command "make production-prepare"

production-install:
	make production-prepare
	sudo mkdir -p ${DJANGO_MEDIA_ROOT}
	sudo mkdir -p ${DJANGO_STATIC_ROOT}
	sudo chown -R ${SYS_DJANGO_USER}:${SYS_DJANGO_GROUP} ${DJANGO_MEDIA_ROOT} ${DJANGO_STATIC_ROOT}
	sudo chmod -R 0775 ${DJANGO_MEDIA_ROOT} ${DJANGO_STATIC_ROOT}
	sudo chmod -R +s ${DJANGO_MEDIA_ROOT} ${DJANGO_STATIC_ROOT}
	sudo cp ${DJANGO_GRORE_APP_ROOT}/production/output/grore.service /etc/systemd/system/grore.service
	sudo systemctl daemon-reload
	sudo systemctl enable --now grore
	sudo nginx -t
	sudo cp ${DJANGO_GRORE_APP_ROOT}/production/output/${WEB_DOMAIN}.conf /etc/nginx/sites-available/${WEB_DOMAIN}.conf
	sudo ln -s /etc/nginx/sites-available/${WEB_DOMAIN}.conf /etc/nginx/sites-enabled/${WEB_DOMAIN}.conf
	sudo nginx -t
	sudo systemctl restart nginx
	certbot --nginx -d ${WEB_DOMAIN} -d www.${WEB_DOMAIN}
	sudo systemctl restart grore nginx

production-install-nix:
	nix-shell scripts/default.nix --command "make production-install"

test-uploaded-images:
	echo "DOESN'T WORK"
	make python
	PYTHONPATH="$PYTONPATH:`pwd`/images/";./venv/bin/python scripts/tests/test_uploaded_images.py
	echo "DOESN'T WORK"

test-uploaded-images-nix:
	nix-shell scripts/default.nix --command "make test-uploaded-images"

docker-compose-up:
	make python
	cd ./scripts/docker
	docker-compose up -d 
	cd ../..

docker-compose-up-nix:
	nix-shell scripts/default.nix --command "make docker-compose-up"

docker-nginx:
	make python
	echo "I don't know how to execute this file scripts/docker/nginx/Dockerfile"

docker-nginx-nix:
	nix-shell scripts/default.nix --command "make docker-nginx"

docker-postgres:
	make python
	echo "I don't know how to execute this file scripts/docker/Dockerfile"

docker-postgres-nix:
	nix-shell scripts/default.nix --command "make docker-postgres"