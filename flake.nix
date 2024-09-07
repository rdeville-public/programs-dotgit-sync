# BEGIN DOTGIT-SYNC BLOCK MANAGED
{
  description = ''
    Flake for DotGit Sync

    Repository helping to manage dotfile for accross git repos in an unified ways.
  '';

  inputs = {
    # Stable Nix Packages
    nixpkgs = {
      url = "nixpkgs/nixos-24.05";
      # url = "github:nixos/nixpkgs/nixos-unstable";
    };
    # Flake Utils Lib
    utils = {
      url = "github:numtide/flake-utils";
    };
    alejandra = {
      url = "github:kamadorueda/alejandra";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    # BEGIN DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_INPUT
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    # END DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_INPUT
  };
  outputs = inputs @ {self, ...}: let
    pkgsForSystem = system:
      import inputs.nixpkgs {
        inherit system;
      };
    # BEGIN DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_CUSTOM_VARS
    # END DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_CUSTOM_VARS
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
    # Formatter for your nix files, available through 'nix fmt'
    # Other options beside 'alejandra' include 'nixpkgs-fmt'
    formatter = forAllSystems (
      system:
        inputs.alejandra.defaultPackage.${system}
    );
    homeManagerModules = {
      dotgit-sync = import ./modules/home-manager.nix self;
    };
    homeManagerModule = self.homeManagerModules.dotgit-sync;

    # BEGIN DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_OUTPUTS_CUSTOM
    packages = forAllSystems (system: let
      pkgs = inputs.nixpkgs.legacyPackages.${system};
      inherit (inputs.poetry2nix.lib.mkPoetry2Nix {inherit pkgs;}) mkPoetryApplication;
    in rec {
      dotgit-sync = mkPoetryApplication {
        projectDir = self;
        preferWheels = true;
      };
      default = self.packages."${system}".dotgit-sync;
    });
    # END DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_OUTPUTS_CUSTOM
  };
}
# END DOTGIT-SYNC BLOCK MANAGED
