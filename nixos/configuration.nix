# ~/dotfiles/nixos/configuration.nix
#
# This file now only contains settings that don't fit
# into the other categories, like enabling flakes.

{ config, lib, pkgs, ... }:

{
  # --- IMPORTANT: Enable Flakes ---
  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  # All other options have been moved to system.nix, services.nix, etc.
  # The 'imports' list is removed because the flake now handles it.
}

