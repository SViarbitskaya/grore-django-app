# Grore Installation Strategy

We use Nixpkgs, not NixOS. To install Nix (multi-user daemon):

https://nixos.org/download/#download-nix

for me this is

`sh <(curl -L https://nixos.org/nix/install) --daemon`

Restart the terminal.

In the repo root (where `default.nix` lives), run:

`nix develop --extra-experimental-features "nix-command flakes" -f default.nix`

(`nix-shell` also reads `default.nix`, but has been unreliable in practice on some Nix client installs — prefer `nix develop -f default.nix`.)

From inside that shell, use the normal `make` targets (`make up`, `make runserver`, ...) — see `doc/makefile.md`.

Create and edit the `.env` configuration file:

`cp scripts/sample.env .env`
then edit `.env` as needed — see `doc/configuration.md` for every variable.

Start the database from Docker (if dev):
check Docker is running: `systemctl status docker`
then `docker compose up -d`, which is set to port 15432.
Or provision a working database if production.

Copy the settings:
`cp grore/settings.py grore/settings_local.py`
and modify parameters as required.
