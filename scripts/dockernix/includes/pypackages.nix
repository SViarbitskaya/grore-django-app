{ pkgs ? import <nixpkgs> {} }:
# Python
(pkgs.python311.withPackages (pyPkgs: [
  pyPkgs.pillow
  pyPkgs.pylibjpeg-libjpeg
  pyPkgs.pypdf2
  pyPkgs.python-ldap
  pyPkgs.pq
  pyPkgs.aiosasl
  pyPkgs.psycopg2
  pyPkgs.bleach
  pyPkgs.cffi
  pyPkgs.chardet
  pyPkgs.django
  pyPkgs.django-formtools
  pyPkgs.django-picklefield
  pyPkgs.django-simple-captcha
  pyPkgs.django-statici18n
  pyPkgs.django-webpack-loader
  pyPkgs.djangorestframework
  pyPkgs.future
  pyPkgs.gunicorn
  pyPkgs.markdown
  pyPkgs.openpyxl
  pyPkgs.pillow
  pyPkgs.pip
  pyPkgs.pycryptodome
  pyPkgs.pyjwt
  pyPkgs.pysaml2
  pyPkgs.python-dateutil
  pyPkgs.python-ldap
  pyPkgs.qrcode
  pyPkgs.requests
  pyPkgs.requests-oauthlib
  pyPkgs.setuptools
  pyPkgs.simplejson
  pyPkgs.python3-gnutls
  pyPkgs.pip
  pyPkgs.venvShellHook
  pyPkgs.pylibjpeg-libjpeg
  pyPkgs.pypdf2
  pyPkgs.pq
  pyPkgs.aiosasl
  pyPkgs.psycopg2
  pyPkgs.python-dotenv
]))