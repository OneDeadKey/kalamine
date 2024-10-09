# A nix alternative to `make dev`, run `nix-build` to build Kalamine on NixOS.

with import <nixpkgs> {};

python3Packages.buildPythonApplication rec {
  pname = "kalamine";
  version = "0.37";
  pyproject = true;

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-MdWP15d4J56ifLli01OIBZqgzpKQZf5f6OcR+3fP0zk=";
  };

  nativeBuildInputs = [
    python3Packages.hatchling
  ];

  propagatedBuildInputs = with python3Packages; [
    click
    livereload
    pyyaml
    tomli
    progress
  ];

  meta = with lib; {
    description = "A cross-platform Keyboard Layout Maker";
    homepage = "https://github.com/OneDeadKey/kalamine";
    license = licenses.mit;
    mainProgram = "kalamine";
  };
}
