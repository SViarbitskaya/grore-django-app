# Grore Integration et Mise en Production

## Integration

https://grore-images.demarchic.com/fr/

Intégration en /home/django/integration

Mise en integration pour tests (mot de passe utilisateur django requis):

```bash
ssh grore-images.com
tmux attach-session
sudo su - django
cd /home/django
./integration.sh
```

## Production

https://grore-images.com/fr/

Production en /home/django/grore-django-app

Mise en production (mot de passe utilisateur django requis):

```bash
ssh grore-images.com
tmux attach-session
sudo su - django
cd /home/django
./up.sh
```