with (import <nixpkgs> {});
  mkShell {
    name = "Grore Shell";

    permittedInsecurePackages = [
      "python3.14-pypdf2-3.0.1"
    ];

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
      python314
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
