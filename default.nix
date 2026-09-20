# Pinned to a specific nixos-26.05 commit via fetchTarball instead of
# resolving <nixpkgs> from whatever channel happens to be configured on the
# local machine. That was resolving inconsistently (root's and django's
# channels on the deploy server had different names/content) and, worse, a
# stale unstable-channel snapshot had its pre-built binaries evicted from
# cache.nixos.org, forcing full from-scratch builds - including
# bootstrapping a compiler toolchain - on every nix-shell invocation
# instead of a normal download. A pinned stable release stays cached far
# longer and is identical on every machine regardless of local config.
let
  nixpkgs = fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/refs/heads/nixos-26.05.tar.gz";
    sha256 = "16fa6vir35h0pajdrs1ws7d3ly28ifks2g9y67y3j7zw1hqyqm3h";
  };
in
with (import nixpkgs {});
  mkShell {
    name = "Grore Shell";

    buildInputs = [
      # Vim confiugred practically
      (
        (vim-full.override {}).customize {
          name = "vim";
          vimrcConfig.customRC = ''
            " your custom vimrc
            set mouse=a
            set nocompatible
            colo torte
            syntax on
            set tabstop     =2
            set softtabstop =2
            set shiftwidth  =2
            set expandtab
            set autoindent
            set smartindent
            " ...
          '';
        }
      )
      # Necessities
      # Matches the Dockerfile's python:3.12-bookworm - not the bleeding-
      # edge python314, which has no prebuilt wheels yet for several
      # scientific packages (pandas, numpy) this project needs, forcing
      # slow/fragile from-source builds that were failing on this server.
      python312
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
      postgresql15Packages.pgvectorscale
    ];
    shellHook = ''
      export LC_ALL="C"
    '';
  }
