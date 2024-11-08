{ pkgs ? import <nixpkgs> { }, ... }:
with pkgs; [
    (import ./vim-configurable.nix {inherit pkgs;})   
    (import ./pypackages.nix {inherit pkgs;})   
    # Necessities
    git
    zlib
    lzlib
    gettext
    # Utilities
    openssl
    curl
    wget
    lynx
    tmux
    netcat
    # Convenance
    dig
    killall
    pwgen
    # # Experimentation
    # docker
    # docker-compose
    # # sqlite
    postgresql_15
  ]
