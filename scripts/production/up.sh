#!/usr/bin/sh
# Script for production automatic update
cd /home/django/grore-django-app
nix-shell default.nix --command "make git-up"
nix-shell default.nix --command "make restart-nix"
