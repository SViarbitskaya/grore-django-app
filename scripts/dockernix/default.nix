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

  nativeBuildInputs = [
    pkgs.makeWrapper
  ];

  installPhase = ''
    mkdir -p $out/bin
    cp $src $out/$pname.tar.gz
    echo "#!/bin/bash" > $out/bin/getgrore 
    echo "tar -xzf $out/$pname.tar.gz" >> $out/bin/getgrore 
    echo "python -m venv .venv" >> $out/bin/getgrore 
    echo "source .venv/bin/activate" >> $out/bin/getgrore 
    echo "cd $name" >> $out/bin/getgrore 
    echo "pip install -r requirements" >> $out/bin/getgrore 
    echo "cp scripts/sample.env .env" >> $out/bin/getgrore 
    chmod +x $out/bin/getgrore
  '';

  postFixup = ''
    wrapProgram $out/bin/getgrore \
      --set PATH ${pkgs.lib.makeBinPath [ pkgs.gnutar pkgs.gzip (import ./includes/pypackages.nix {inherit pkgs;}) ]}
  '';

  meta = with pkgs.lib; {
    description = "Django site on grore-images.com";
    homepage = "https://github.com/SViarbitskaya/app";
    platforms = platforms.unix;
  };


} 