with import <nixpkgs> {};
# { lib
# , fetchPypi
# , python3Packages
# }:

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
    # maintainers = with maintainers; [ marsam ];
    mainProgram = "kalamine";
  };
}
