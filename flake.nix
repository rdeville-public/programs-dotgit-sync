{
  description = ''
    Flake for DotGit Sync

    Repository helping to manage dotfile for across git repos in an unified ways.
  '';

  inputs = {
    nixpkgs = {
      url = "nixpkgs/nixos-24.05";
    };
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs = inputs @ {self, ...}: let
    pkgsForSystem = system:
      import inputs.nixpkgs {
        inherit system;
      };
    # This is a function that generates an attribute by calling a function you
    # pass to it, with each system as an argument
    forAllSystems = inputs.nixpkgs.lib.genAttrs allSystems;

    allSystems = [
      "x86_64-linux"
      "aarch64-linux"
      "x86_64-darwin"
      "aarch64-darwin"
    ];
  in {
    # TOOLING
    # ========================================================================
    formatter = forAllSystems (
      system:
        (pkgsForSystem system).alejandra
    );

    # PACKAGES
    # ========================================================================
    packages = forAllSystems (system: let
      pkgs = inputs.nixpkgs.legacyPackages.${system};
      inherit (inputs.poetry2nix.lib.mkPoetry2Nix {inherit pkgs;}) mkPoetryApplication;
    in {
      dotgit-sync = mkPoetryApplication {
        projectDir = self;
        preferWheels = true;
      };
      default = self.packages."${system}".dotgit-sync;
    });

    # HOME MANAGER MODULES
    # ========================================================================
    homeManagerModules = {
      dotgit-sync = import ./modules/home-manager.nix self;
    };
    homeManagerModule = self.homeManagerModules.awesomerc;

  };
}
