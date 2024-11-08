{ pkgs ? import <nixpkgs> {} }:
# Vim confiugred practically
((pkgs.vim_configurable.override {  }).customize{
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