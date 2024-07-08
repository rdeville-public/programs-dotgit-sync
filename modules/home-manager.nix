# BEGIN DOTGIT-SYNC BLOCK MANAGED
self: {
  pkgs,
  lib,
  config,
  # BEGIN DOTGIT-SYNC BLOCK EXCLUDED NIX_HOME_MANAGER_MODULE_CUSTOM
  ...
}: let
  cfg = config.dotgit-sync;
in
{
  options = {
    dotgit-sync = {
      enable = lib.mkEnableOption "Install DotGit Sync Package";
    };
  };

  config = lib.mkIf cfg.enable {
    home = {
      packages = [
        self.packages.${pkgs.stdenv.hostPlatform.system}.default
      ];
    };
  };
  # END DOTGIT-SYNC BLOCK EXCLUDED NIX_HOME_MANAGER_MODULE_CUSTOM
}
# END DOTGIT-SYNC BLOCK MANAGED
