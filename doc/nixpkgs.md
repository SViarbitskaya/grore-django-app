# NIXPKGS

We use NIXPKGS and not NIXOS. To install Nixpkgs (multi-user daemon) :

https://nixos.org/download/#download-nix

for me this is 

`sh <(curl -L https://nixos.org/nix/install) --daemon`

Restart the terminal 

in the same folder as `nix.shell`, run 

`nix-shell`

then a typical python virtual environment

`python -m venv venv`

activate the venv

`source venv/bin/activate`

create and edit the .env configuration file:

`cp scripts/sample.env .env`  
puis modifier .env selon les besoins

start the database from docker (if dev)  
check to see if docker is running :  
`systemctl status docker`  
and then start the posgresql database (if dev)
`docker compose up -d`  
which is set to port 15432
or provision a working database if production

Copy the settings    
`cp grore/settings.py grore/settings_local.py`  
and modify parameters as required 
