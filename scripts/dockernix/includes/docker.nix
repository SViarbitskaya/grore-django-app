{ pkgs ? import <nixpkgs> { }
, pkgsLinux ? import <nixpkgs> { system = "x86_64-linux"; }
}:
let
  djangoGroreApp = pkgs.callPackage ./../default.nix;
  djangoRequirements = pkgs.callPackage ./src.nix;
in
pkgs.dockerTools.buildImage {
  name = "grore-django-app";
  tag = "nix";
  config = {
    WorkingDir = builtins.getEnv "APP_DJANGO_ROOT";
    # Env = [
    #   {APP_DJANGO_ROOT = builtins.getEnv "APP_DJANGO_ROOT";}
    #   {APP_DJANGO_USER_USER = builtins.getEnv "APP_DJANGO_USER_USER";}
    #   {APP_DJANGO_USER_GROUP = builtins.getEnv "APP_DJANGO_USER_GROUP";}
    #   {APP_DJANGO_USER_UID = builtins.getEnv "APP_DJANGO_USER_UID";}
    #   {APP_DJANGO_USER_GID = builtins.getEnv "APP_DJANGO_USER_GID";}
    #   {PYTHONDONTWRITEBYTECODE = 1;}
    #   {PYTHONUNBUFFERED = 1;}
    # ];
    Cmd = [ "/bin/hello" ];
  };
  # copyToRoot = pkgs.buildEnv {
  #   name = "grore";
  #   paths = [ djangoGroreApp ];
  #   pathsToLink = [ ];
  # };
  copyToRoot = pkgs.buildEnv {
    name = "image-root";
    paths = [ pkgs.hello ];
    pathsToLink = [ "/bin" ];
  };
  # copyToRoot = ./../../..;
  # "./requirements.txt ."
  runAsRoot = ''
    # apt-get update && apt-get install -y netcat sudo
    # addgroup --system --gid $APP_DJANGO_USER_GID $APP_DJANGO_USER_GROUP && adduser --system --uid $APP_DJANGO_USER_UID --group $APP_DJANGO_USER_USER
    # install dependencies
    # pip install --upgrade pip
    # pip install -r requirements.txt
    # cat /requirements/requirements.txt
  '';
}