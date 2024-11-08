{ pkgs ? import <nixpkgs> { }, ... }:
pkgs.stdenv.mkDerivation {
  name = "grore-django-app-0.1.2-alpha";
  pname = "grore-django-app";
  version = "0.1.2-alpha";
  src = pkgs.fetchFromGitHub {
    owner = "SViarbitskaya";
    repo = "grore-django-app";
    rev = "695865fde1a5c1a8328ff3be6a272d2a08e17be0";
    hash = "sha256-aiuhZYTAtF4uic40J9KjrexBsc9NlMWMSRIfInA/t+A=";
  };
  dontBuild = true;
  buildInputs = (import ./includes/build-inputs.nix { inherit pkgs; });

  nativeBuildInputs = [
    pkgs.makeWrapper
  ];

  installPhase = ''
    mkdir -p $out/bin
    cp -r $src $out
    echo "#!/bin/bash" > $out/bin/grore-init 
    echo "if ! [ -z \"\$( ls -A './' )\" ]; then" >> $out/bin/grore-init 
    echo "  echo \"Directory must be empty for $name\"" >> $out/bin/grore-init 
    echo "  exit 1" >> $out/bin/grore-init 
    echo "fi" >> $out/bin/grore-init 
    echo "cp -r $out $name" >> $out/bin/grore-init 
    echo "chmod ug+w -R $name" >> $out/bin/grore-init 
    echo "mkdir -p ./$name/.cache" >> $out/bin/grore-init 
    echo "python -m venv ./$name/.cache/.venv" >> $out/bin/grore-init 
    echo "./$name/.cache/.venv/bin/pip install --upgrade pip" >> $out/bin/grore-init 
    echo "./$name/.cache/.venv/bin/pip install -r $name/requirements.txt" >> $out/bin/grore-init 
    echo "cp $name/scripts/sample.env $name/.env" >> $out/bin/grore-init 
    echo "source $name/.cache/.venv/bin/activate" >> $out/bin/grore-init 
    echo "echo \"\"" >> $out/bin/grore-init 
    echo "echo \"\"" >> $out/bin/grore-init 
    echo "echo \"To use $name, execute the following lines\"" >> $out/bin/grore-init 
    echo "echo \"\"" >> $out/bin/grore-init 
    echo "echo \"source \`pwd\`/$name/.cache/.venv/bin/activate\"" >> $out/bin/grore-init 
    echo "echo \"cd $name \"" >> $out/bin/grore-init 
    echo "echo \"vi .env \"" >> $out/bin/grore-init 
    echo "echo \"python manage.py migrate \"" >> $out/bin/grore-init 
    echo "echo \"python manage.py loaddata scripts/data/classeur.json \"" >> $out/bin/grore-init 
    echo "echo \"python manage.py loaddata scripts/data/page_fixtures.json \"" >> $out/bin/grore-init 
    echo "echo \"python manage.py runserver \"" >> $out/bin/grore-init 
    echo "cd ./$name" >> $out/bin/grore-init 
    echo "echo \"\"" >> $out/bin/grore-init 
    echo "echo \"\"" >> $out/bin/grore-init 
    chmod +x $out/bin/grore-init
  '';

  postFixup = ''
    wrapProgram $out/bin/grore-init \
      --set PATH ${pkgs.lib.makeBinPath [ pkgs.gnutar pkgs.gzip pkgs.coreutils  (import ./includes/pypackages.nix {inherit pkgs;}) ]}
  '';

  meta = with pkgs.lib; {
    description = "Django site on grore-images.com";
    homepage = "https://github.com/SViarbitskaya/app";
    platforms = platforms.unix;
  };


} 