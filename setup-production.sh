source .env
sudo mkdir -p ${DJANGO_MEDIA_ROOT}
sudo mkdir -p ${DJANGO_STATIC_ROOT}
sudo chown -R ${SYS_DJANGO_USER}:${SYS_DJANGO_GROUP} ${DJANGO_MEDIA_ROOT} ${DJANGO_STATIC_ROOT}
sudo chmod -R 0775 ${DJANGO_MEDIA_ROOT} ${DJANGO_STATIC_ROOT}
sudo chmod -R +s ${DJANGO_MEDIA_ROOT} ${DJANGO_STATIC_ROOT}
sduo ln -s `pwd`/grore.service /etc/systemd/system/grore.service
sudo systemctl daemon-reload
sudo systemctl enable --now grore
sudo nginx -t
