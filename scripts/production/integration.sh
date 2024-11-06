#!/usr/bin/sh
# Script for ingeration automatic update from /home/django
cd /home/django/integration
nix-shell default.nix --command "make git-up"
sudo /usr/bin/systemctl restart grore-images.demarchic.com.service
