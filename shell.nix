let pkgs = import (builtins.fetchTarball {
      url = "https://github.com/costrouc/nixpkgs/archive/46976eff15c48713f2aa99bdbafa8229cb031262.tar.gz";
      sha256 = "1q32jjv87n4dqchi00bj11bmy99pp72qdy3wy4c4fqxxchh63y38";
    }) { };

    pythonPackages = pkgs.python3Packages;
in
pkgs.mkShell {
  buildInputs = with pythonPackages; [ pkgs.sqlite datasette pytest];

  shellHook = ''
    export SQLITE_TMPDIR=/tmp
  '';
}
