# ~/dotfiles/nixos/packages.nix
#
# This file lists all system-wide packages and fonts.

{ config, pkgs, ... }:

{
  # --- System Packages ---
  environment.systemPackages = with pkgs; [
    vim
    wget
    nodejs 
    nodePackages.live-server 
    neovim
    pfetch
    flameshot
    dunst
    git
    rofi
    libnotify
    firefox
    pcmanfm
    gcc
    alacritty
    xwallpaper
    pavucontrol
    feh
    (python3.withPackages (ps: [
      ps.psutil
      ps.pulsectl
    ]))
  ];

  # --- System Fonts ---
  fonts.packages = with pkgs; [
    (nerdfonts.override { fonts = [ "FiraCode" "JetBrainsMono" ]; })
    font-awesome
  ];
}

