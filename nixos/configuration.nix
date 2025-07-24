# ~/dotfiles/nixos/configuration.nix

{ config, lib, pkgs, ... }:

{
  # --- IMPORTANT: Enable Flakes ---
  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  imports = [ ./hardware-configuration.nix ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.networkmanager.enable = true;
  time.timeZone = "Europe/Budapest";
  i18n.defaultLocale = "hu_HU.UTF-8";

  # --- Sound Server ---
  # This enables the modern PipeWire sound server.
  sound.enable = true;
  hardware.pulseaudio.enable = false; # Ensure pulseaudio is not running
  security.rtkit.enable = true; # Real-time permissions for PipeWire
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

  services.picom.enable = true;

  users.users.balint = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
  };

  environment.systemPackages = with pkgs; [
    vim
    wget
    neovim
    feh
    pfetch
    flameshot
    git
    rofi
    firefox
    pcmanfm
    gcc
    alacritty
    xwallpaper
    pavucontrol # A graphical mixer to control volume and devices
    (python3.withPackages (ps: [
      ps.psutil
      ps.pulsectl
    ]))
  ];

  programs.git = {
    enable = true;
    config = {
      credential.helper = "store";
    };
  };

  fonts.packages = with pkgs; [
    (nerdfonts.override { fonts = [ "FiraCode" "JetBrainsMono" ]; })
    font-awesome
  ];
  
  system.stateVersion = "24.05";
}

