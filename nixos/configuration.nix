# ~/dotfiles/nixos/configuration.nix
#
# This is the main entry point for the system configuration.
# It simply imports all the other modules.

{ config, lib, pkgs, ... }:

{
  # --- IMPORTANT: Enable Flakes ---
  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  # --- ADDED: Allow installation of specific unfree packages ---
  # This is safer than allowing all unfree packages.
  nixpkgs.config.allowUnfreePredicate = pkg: builtins.elem (lib.getName pkg) [
    "vscode"
    # You can add other unfree packages here in the future, e.g., "steam"
  ];

  # --- Import all other configuration modules ---
  imports =
    [
      ./hardware-configuration.nix
      ./system.nix
      ./services.nix
      ./packages.nix
    ];
}

