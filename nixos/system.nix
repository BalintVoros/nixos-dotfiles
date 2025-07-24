# ~/dotfiles/nixos/system.nix
#
# This file contains core system settings.

{ config, pkgs, ... }:

{
  # --- Bootloader ---
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  # --- Networking ---
  networking.networkmanager.enable = true;

  # --- Time & Localization ---
  time.timeZone = "Europe/Budapest";
  i18n.defaultLocale = "hu_HU.UTF-8";

  # --- User Account ---
  users.users.balint = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
  };
  
  # --- Git Settings ---
  programs.git = {
    enable = true;
    config = {
      credential.helper = "store";
    };
  };

  # --- System State ---
  system.stateVersion = "24.05";
}

