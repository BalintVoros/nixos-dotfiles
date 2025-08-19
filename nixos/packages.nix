# ~/dotfiles/nixos/packages.nix
#
# This file lists all system-wide packages and fonts.

{ config, pkgs, ... }:

{
  # --- System Packages ---
  environment.systemPackages = with pkgs; [
    # Your existing packages
    vim
    wget
    neovim
    pfetch
    flameshot
    git
    rofi
    firefox
    pcmanfm
    gcc
    alacritty
    xwallpaper
    pavucontrol
    feh
    dunst
    libnotify
    nodejs
    nodePackages.live-server
    vscode


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

