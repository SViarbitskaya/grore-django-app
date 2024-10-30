source ../.env
echo "" > "./output/template.sh" 
IFS=$'\n'
for i in `cat ../.env`                                                                                                             ✔ 
do
  if [[ ${#i} -gt 4 ]] ; then
    echo -n $i >> "./output/template.sh" 
    echo -n " " >> "./output/template.sh" 
  fi
done
cp ./output/template.sh ./output/template-nginx.sh
echo -n " envsubst < grore-nginx.conf.template > ./output/${WEB_DOMAIN}.conf" >> "./output/template-nginx.sh" 
source ./output/template-nginx.sh
rm ./output/template-nginx.sh
cp ./output/template.sh ./output/template-service.sh
echo -n " envsubst < grore.service.template > ./output/grore.service" >> "./output/template-service.sh"
source ./output/template-service.sh
rm ./output/template-service.sh
rm ./output/template.sh
cat << EOF
# MERCI DEFAIRE LES COMMANDES SUIVANTES AUSSI
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
EOF