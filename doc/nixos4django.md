# Mess House Nixos Django Deployment

```bash
[nix-shell:~/messhouse]# su - django

[django@nixos:~]$ python3 --version
Python 3.11.8

[django@nixos:~]$ python3 -m venv venv

6: venet0@if105: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether e2:af:3a:ed:7c:10 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 37.205.14.63/32 scope global venet0
       valid_lft forever preferred_lft forever
    inet6 2a03:3b40:fe:7d7::1/64 scope global
       valid_lft forever preferred_lft forever
    inet6 fe80::e0af:3aff:feed:7c10/64 scope link proto kernel_ll
       valid_lft forever preferred_lft forever



IP v4: 37.205.14.63

IP v6: 2a03:3b40:fe:7d7::1

ssh django@37.205.14.63

git clone https://www.github.com/SViarbitskya/grore-django-app

source ./venv/bin/activate

cd grore-django-app

pip install -r requirements.txt

git pull

git branch origin develop

[django@nixos:~]$ source venv/bin/activate
(venv)
[django@nixos:~]$ pip install gunicorn
Collecting gunicorn
  Downloading gunicorn-21.2.0-py3-none-any.whl.metadata (4.1 kB)
Collecting packaging (from gunicorn)
  Using cached packaging-24.0-py3-none-any.whl.metadata (3.2 kB)
Downloading gunicorn-21.2.0-py3-none-any.whl (80 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 80.2/80.2 kB 3.8 MB/s eta 0:00:00
Using cached packaging-24.0-py3-none-any.whl (53 kB)
Installing collected packages: packaging, gunicorn
Successfully installed gunicorn-21.2.0 packaging-24.0
(venv)


```


Postgres

```psql
GRANT CONNECT ON DATABASE grore to groreuser;
GRANT ALL ON SCHEMA public TO groreuser;
ALTER ROLE groreuser SET client_encoding TO 'utf8';
ALTER ROLE groreuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE groreuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE grore TO groreuser;
ALTER USER grore WITH PASSWORD 'CHANGE_ME';
```



