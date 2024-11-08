let
  pkgs = import <nixpkgs> { };
in
pkgs.stdenv.mkDerivation {
  name = "requirements-txt";
  system = builtins.currentSystem; 
  src = ./.;
  # phases = ["unpackPhase" "installPhase"];
  installPhase = ''
    mkdir -p $out/requirements
    cp ./requirements.txt $out/requirements/requirements.txt 
  ''; 
}