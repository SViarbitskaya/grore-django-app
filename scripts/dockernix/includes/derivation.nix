{ pkgs ? import <nixpkgs> { }, ... }:
let 
  dockerImage = pkgs.callPackage ./docker.nix { };
in
pkgs.stdenv.mkDerivation {
  name = "django-grore-app-docker";
  src = ./.;
  buildInputs = with pkgs; [
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
    # Experimentation
    docker
    docker-compose
    # sqlite
    postgresql_15
  ];

  phases = ["unpackPhase" "buildPhase"];
  buildPhase = ''
    mkdir -p $out/
    cp ${dockerImage} $out/docker-image.tar.gz 
  '';
  shellHook = ''
    mkdir -p .cache
    export dockerfile=`nix-build docker.nix`
    echo $dockerfile
  '';
}