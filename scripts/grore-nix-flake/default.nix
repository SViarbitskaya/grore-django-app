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
    echo "#!/bin/bash" > $out/bin/getgrore 
    echo "if ! [ -z \"\$( ls -A './' )\" ]; then" >> $out/bin/getgrore 
    echo "  echo \"Directory must be empty for $name\"" >> $out/bin/getgrore 
    echo "  exit 1" >> $out/bin/getgrore 
    echo "fi" >> $out/bin/getgrore 
    echo "cp -r $out $name" >> $out/bin/getgrore 
    echo "chmod ug+w -R $name" >> $out/bin/getgrore 
    echo "mkdir -p ./$name/.cache" >> $out/bin/getgrore     
    echo "python -m venv ./$name/.cache/.venv" >> $out/bin/getgrore 
    echo "./$name/.cache/.venv/bin/pip install --upgrade pip" >> $out/bin/getgrore 
    echo "./$name/.cache/.venv/bin/pip install -r $name/requirements.txt" >> $out/bin/getgrore 
    echo "cp $name/scripts/sample.env $name/.env" >> $out/bin/getgrore 
    echo "source $name/.cache/.venv/bin/activate" >> $out/bin/getgrore 
    echo "echo \"\"" >> $out/bin/getgrore 
    echo "echo \"\"" >> $out/bin/getgrore 
    echo "echo \"To use $name, execute the following lines\"" >> $out/bin/getgrore 
    echo "echo \"\"" >> $out/bin/getgrore 
    echo "echo \"source \`pwd\`/$name/.cache/.venv/bin/activate\"" >> $out/bin/getgrore 
    echo "echo \"cd $name \"" >> $out/bin/getgrore 
    echo "echo \"vi .env \"" >> $out/bin/getgrore 
    echo "echo \"python manage.py migrate \"" >> $out/bin/getgrore 
    echo "echo \"python manage.py loaddata scripts/data/classeur.json \"" >> $out/bin/getgrore 
    echo "echo \"python manage.py loaddata scripts/data/page_fixtures.json \"" >> $out/bin/getgrore 
    echo "echo \"python manage.py runserver \"" >> $out/bin/getgrore 
    echo "cd ./$name" >> $out/bin/getgrore 
    echo "echo \"\"" >> $out/bin/getgrore 
    echo "echo \"\"" >> $out/bin/getgrore 
    chmod +x $out/bin/getgrore
  '';

  postFixup = ''
    wrapProgram $out/bin/getgrore \
      --set PATH ${pkgs.lib.makeBinPath [ pkgs.gnutar pkgs.gzip pkgs.coreutils  (import ./includes/pypackages.nix {inherit pkgs;}) ]}
  '';

  meta = with pkgs.lib; {
    description = "Django site on grore-images.com";
    homepage = "https://github.com/SViarbitskaya/app";
    platforms = platforms.unix;
  };


} 