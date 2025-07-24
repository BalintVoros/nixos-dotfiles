{ config, lib, pkgs, ... }:
let
  home-manager = builtins.fetchTarball "https://github.com/nix-community/home-manager/archive/release-25.05.tar.gz";
in
{
  imports =
    [ 
      ./hardware-configuration.nix
      (import "${home-manager}/nixos")
    ];
    home-manager.useUserPackages = true;
    home-manager.useGlobalPkgs =  true;
    home-manager.backupFileExtension = "backup";
    home-manager.users.balint = import ./home.nix;

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  networking.networkmanager.enable = true;
  time.timeZone = "Europe/Budapest";
  i18n.defaultLocale = "hu_HU.UTF-8";

  services.xserver = {
    enable = true;
    windowManager.qtile.enable = true;
    displayManager.defaultSession = "qtile";
    displayManager.sessionCommands = ''
    xwallpaper --zoom ~/Downloads/animeskull.png
    xset r rate 200 35 &
    '';
xkb.layout = "hu";
  };

  services.picom.enable = true;

  users.users.balint= {
     isNormalUser = true;
     extraGroups = [ "wheel" ]; 
  };

  environment.systemPackages = with pkgs; [
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
   # Updated Python environment to include the necessary library for the email script
   (python3.withPackages (ps: [
     ps.psutil 
     ps.pulsectl
     # The imaplib is part of standard library, so no extra package is needed.
     # This structure is kept for consistency.
   ]))
 ];

  fonts.packages = with pkgs; [
    nerd-fonts.fira-code
    nerd-fonts.jetbrains-mono
    font-awesome
  ];
  
  system.stateVersion = "25.05";
}

