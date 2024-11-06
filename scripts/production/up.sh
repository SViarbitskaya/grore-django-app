#!/usr/bin/sh
# Script for production automatic update from /home/django
cd /home/django/grore-django-app
nix-shell default.nix --command "make git-up"
sudo /usr/bin/systemctl restart grore
