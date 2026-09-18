with import <nixpkgs> {};
with pkgs.python311Packages;

let project_root = builtins.getEnv "PWD"; in
buildPythonPackage rec {
    name = "kalamine";
    format = "pyproject";
    src = ./.;

    propagatedBuildInputs = [
        # setup dependencies
        hatchling

        # run-time dependencies
        click
        livereload
        pyyaml
        tomli
        progress

        # dev dependencies
        black
        isort
        pkgs.ruff
        pytest
        lxml
        mypy
        types-pyyaml
    ];

    # HACK: replace duplicated src files with a symbolic link to the original
    # src files, in order to not transform python into a compiled language.
    postInstall = ''
        rm -rf $out/lib/python3.11/site-packages/kalamine
        ln -s ${project_root}/kalamine $out/lib/python3.11/site-packages/kalamine
    '';
}
