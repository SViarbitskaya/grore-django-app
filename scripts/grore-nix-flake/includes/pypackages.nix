{ pkgs ? import <nixpkgs> {} }:
# Python
(pkgs.python311.withPackages (pyPkgs: [
  pyPkgs.aiosasl
  pyPkgs.bleach
  pyPkgs.cffi
  pyPkgs.chardet
  pyPkgs.django
  pyPkgs.django-appconf
  pyPkgs.django-compressor
  pyPkgs.django-debug-toolbar
  pyPkgs.django-formtools
  pyPkgs.django-modeltranslation
  pyPkgs.django-picklefield
  pyPkgs.django-simple-captcha
  pyPkgs.django-statici18n
  pyPkgs.django-webpack-loader
  pyPkgs.djangorestframework
  pyPkgs.future
  pyPkgs.gunicorn
  pyPkgs.markdown
  pyPkgs.numpy
  pyPkgs.openpyxl
  pyPkgs.pandas
  pyPkgs.pillow
  pyPkgs.pip
  pyPkgs.pq
  pyPkgs.psycopg2
  pyPkgs.pycryptodome
  pyPkgs.pyjwt
  pyPkgs.pylibjpeg-libjpeg
  pyPkgs.pypdf2
  pyPkgs.pysaml2
  pyPkgs.python-dateutil
  pyPkgs.python-dotenv
  pyPkgs.python-ldap
  pyPkgs.python3-gnutls
  pyPkgs.pytz
  pyPkgs.qrcode
  pyPkgs.rcssmin
  pyPkgs.requests
  pyPkgs.requests-oauthlib
  pyPkgs.rjsmin
  pyPkgs.setuptools
  pyPkgs.simplejson
  pyPkgs.six
  pyPkgs.sqlparse
  pyPkgs.typing-extensions
  pyPkgs.tzdata
  pyPkgs.venvShellHook
]))