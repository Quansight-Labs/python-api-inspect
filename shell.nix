{ pkgs ? import <nixpkgs> { }, pythonPackages ? pkgs.python3Packages }:

pkgs.mkShell {
  buildInputs = [ pkgs.sqlite pkgs.python3Packages.pandas ];

  shellHook = ''
    export SQLITE_TMPDIR=/tmp
  '';
}
