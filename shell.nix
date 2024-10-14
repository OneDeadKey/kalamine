{ pkgs ? import <nixpkgs> {} }:

let project_root = builtins.getEnv "PWD"; in
pkgs.mkShell {
    name = "kalamine-dev-shell";
    shellHook = ''
        nix-build
        export PATH=${project_root}/result/bin:$PATH
    '';
}
