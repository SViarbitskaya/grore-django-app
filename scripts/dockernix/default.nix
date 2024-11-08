{ pkgs ? import <nixpkgs> { }, ... }:
pkgs.stdenv.mkDerivation {
  name = "grore-django-app-0.1.1";
  pname = "grore-django-app";
  version = "0.1.1";
  src = pkgs.fetchurl {
    url = "https://github.com/SViarbitskaya/grore-django-app/archive/refs/tags/0.1.1.tar.gz";
    sha256 = "sha256-v/HUnBljhWdfuu3EKRXLJTXGl1bueXVoXIA1TfUiRtE=";
  };
  dontBuild = true;
  buildInputs = (import ./includes/build-inputs.nix { inherit pkgs; });

  outputs = ["bin" "grore-django-app"];

  installPhase = ''
    mkdir -p $bin
    mkdir -p $grore-django-app
    cp $src $grore-django-app/$pname.tar.gz
    echo "tar -xzf $grore-django-app/$pname.tar.gz" > $bin/getgrore.sh
    chmod +x $bin/getgrore.sh
  '';

  meta = with pkgs.lib; {
    description = "Django site on grore-images.com";
    homepage = "https://github.com/SViarbitskaya/grore-django-app";
    platforms = platforms.unix;
  };


} 