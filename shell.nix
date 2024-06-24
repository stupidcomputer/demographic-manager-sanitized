# thanks nixos wiki
{ pkgs ? import <nixpkgs> {} }:

let
  my-python-packages = ps: with ps; [
    openpyxl
  ];
in
  pkgs.mkShell {
    packages = [
      (pkgs.python3.withPackages my-python-packages)
      pkgs.libreoffice
    ];
  }
