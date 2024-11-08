{
  description = "Creates docker image for Grore-Django-App";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachDefaultSystem (
    system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      myDockerImage = pkgs.callPackage ./includes/docker.nix { };
    in
    {
      packages.default = pkgs.callPackage ./default.nix { myDockerImage = myDockerImage };
    }
  );
}