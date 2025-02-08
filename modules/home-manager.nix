self: {
  pkgs,
  lib,
  config,
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
}
