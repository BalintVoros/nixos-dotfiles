# ~/dotfiles/nixos/services.nix
#
# This file enables system-level services.

{ config, pkgs, ... }:

{
  # --- Sound Server ---
  sound.enable = true;
  hardware.pulseaudio.enable = false;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    pulse.enable = true;
  };

  # --- X11 Server ---
  services.xserver = {
    enable = true;
    windowManager.qtile.enable = true;
    displayManager.defaultSession = "none+qtile";
    xkb.layout = "hu";
  };

  # --- Compositor ---
  services.picom.enable = true;
}

