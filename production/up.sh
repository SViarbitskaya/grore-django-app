# Continuous deployment script
# meant to be run by django
# I copy it to /home/django/up.sh such that it is out of the repository
# The access is via 
# ssh django@grore-images.com '/home/django/up.sh'
# Assuming that 
# django@grore-images.com:/home/django/.ssh/authorized_keys
# has the id_rsa.pub equivalent to the id_rsa used by the calling agent.
# Also used by .github/workflows/up.yml continuous deployement script
# 
source /home/django/grore-django-app/.env
cd /home/django/grore-django-app/grore-django-app
/nix/var/nix/profiles/default/bin/nix-shell
sudo /usr/bin/systemctl restart grore
exit
