# BEGIN DOTGIT-SYNC BLOCK MANAGED
{
  description = ''
    Flake for DotGit Sync

    Repository helping to manage dotfile for accross git repos in an unified ways.
  '';

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

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
      url = "github:kamadorueda/alejandra/3.0.0";
      inputs.nixpkgs.follows = "nixpkgs";
    };
# BEGIN DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_INPUT
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
# END DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_INPUT
  };

  outputs = inputs @ {
    self,
    utils,
    nixpkgs,
    alejandra,
# BEGIN DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_OUTPUTS_VARS
    #
# END DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_OUTPUTS_VARS
    ...
  }: let
    pkgsForSystem = system:
      import nixpkgs {
        inherit system;
      };

    # This is a function that generates an attribute by calling a function you
    # pass to it, with each system as an argument
    forAllSystems = nixpkgs.lib.genAttrs allSystems;

    allSystems = [
      "x86_64-linux"
      "aarch64-linux"
      "x86_64-darwin"
      "aarch64-darwin"
    ];
  in
    {
      # TOOLING
      # ========================================================================
      # Formatter for your nix files, available through 'nix fmt'
      # Other options beside 'alejandra' include 'nixpkgs-fmt'
      formatter = forAllSystems (
        system:
          alejandra.defaultPackage.${system}
      );

      overlays.default = final: prev: {
        dotgit-sync = final.callPackage ./package.nix {};
      };
# BEGIN DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_OUTPUTS_PACKAGES
      packages = forAllSystems (system: let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (inputs.poetry2nix.lib.mkPoetry2Nix {inherit pkgs;}) mkPoetryApplication;
      in rec {
        dotgit-sync = mkPoetryApplication {
          projectDir = self;
          preferWheels = true;
        };
        default = self.packages."${system}".dotgit-sync;
      });
# END DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_OUTPUTS_PACKAGES


# BEGIN DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_OUTPUTS_CUSTOM

# END DOTGIT-SYNC BLOCK EXCLUDED NIX_FLAKE_OUTPUTS_CUSTOM
    };
}
# END DOTGIT-SYNC BLOCK MANAGED
