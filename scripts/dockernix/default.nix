{ pkgs ? import <nixpkgs> { }, ... }:
let 
  myDockerImage = pkgs.callPackage ./includes/docker.nix { };
in 
pkgs.stdenv.mkDerivation {
  name = "grore";
  src = ./.;
  buildInputs = with pkgs; [
    (import ./includes/vim-configurable.nix {inherit pkgs;})   
    (import ./includes/pypackages.nix {inherit pkgs;})   
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
    # Experimentation
    docker
    docker-compose
    # sqlite
    postgresql_15
  ];
  
  phases = ["unpackPhase" "installPhase"];
  installPhase = ''
    mkdir -p $out/
    cp ${myDockerImage} $out/docker-grore-django-app.tar.gz 
  ''; 
  shellHook = ''
    mkdir -p .cache
    echo ${myDockerImage}
  '';
}