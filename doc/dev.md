# GRORE Development

https://github.com/SViarbitskaya/grore-django-app

https://github.com/chris2fr/grore-django-app

https://grore.resdigita.com/en/

Update from root: 

`./upgrore.sh`

To get the django project:

```bash
systemctl stop django
su - django
source /home/django/venv/bin/activate
cd grore-django-app
git pull
python manage.py makemigrations
python manage.py migrate
exit 
systemctl start django
```

## settings.py

```python

ALLOWED_HOSTS = [
  'localhost',
  '127.0.0.1',
]


# Deactivate Debug Toolbar

#    'debug_toolbar.middleware.DebugToolbarMiddleware',
#                'django.template.context_processors.debug',

# Adjust static URL et Root

STATIC_URL = '/static/'
STATIC_ROOT =  os.path.join(BASE_DIR, 'static')
#STATICFILES_DIRS = [
#  '/home/django/grore-django-app/static',
#]


CSRF_TRUSTED_ORIGINS = ['https://grore.resdigita.com']
```

https://github.com/chris2fr/grore-django-app/commit/83ddd6737d037a631d305daa492963838bf89877

https://github.com/chris2fr/grore-django-app/commit/08a8b7fea451a293fd5240d8ae8272078a15a882

## MESSHOUSE

Accès développement:  
`ssh django@grore.resdigita.com`  
`ssh root@grore.resdigita.com`



Les utilisateurs sont root, django et grore. 

Django is installed as a system service `django` and can be checked by `systemctl status django`.

Repository for the configuration du serveur:  
https://github.com/chris2fr/messhouse

Informations on configuration in the wiki:  
https://github.com/chris2fr/messhouse/wiki

Spécifications su serveur:  
https://www.mann.fr/documents/5/doc-20240507-config-server-django-grore.pdf

Tabelau de bord pour le serveur (pour Chris):  
https://vpsadmin.vpsfree.cz/

