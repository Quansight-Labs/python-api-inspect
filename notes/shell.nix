{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = [ pkgs.sqlite pkgs.python3Packages.pandas ];

  shellHook = ''
    export SQLITE_TMPDIR=/tmp
  '';
}
