# ~/dotfiles/nixos/home.nix
{config, pkgs, ...}:

{
  home.username = "balint";
  home.homeDirectory = "/home/balint";
  home.stateVersion = "24.05";

  programs.zsh = {
    enable = true;
    oh-my-zsh = {
      enable = true;
      theme = "agnoster";
      # This list is now only for plugins that come with Oh My Zsh
      plugins = [ "git" ];
    };

    # --- MODIFIED: This is the correct way to add external plugins ---
    plugins = [
      {
        name = "zsh-autosuggestions";
        src = pkgs.zsh-autosuggestions;
      }
      {
        name = "zsh-syntax-highlighting";
        src = pkgs.zsh-syntax-highlighting;
      }
    ];

    shellAliases = {
      btw = "echo nixos";
      nrs = "cd ~/dotfiles && sudo nixos-rebuild switch --flake .#nixos";
      nix = "sudo -E nvim /etc/nixos/configuration.nix";
      qtile = "sudo -E nvim ~/.config/qtile/config.py";
      homenix= "sudo -E nvim /etc/nixos/home.nix";
    };
  };

  programs.alacritty = {
    enable = true;
    settings = {
      shell = {
        program = "${pkgs.zsh}/bin/zsh";
        args = [ "-l" ];
      };
      window = { padding = { x = 10; y = 10; }; opacity = 0.95; };
      font = {
        normal = { family = "FiraCode Nerd Font"; style = "Regular"; };
        bold = { family = "FiraCode Nerd Font"; style = "Bold"; };
        italic = { family = "FiraCode Nerd Font"; style = "Italic"; };
        size = 12;
      };
      cursor = { style = { shape = "Block"; blinking = "On"; }; };
      colors = {
        primary = { background = "#282a36"; foreground = "#f8f8f2"; };
        cursor = { text = "#282a36"; cursor = "#f8f8f2"; };
        selection = { text = "#f8f8f2"; background = "#44475a"; };
        normal = { black = "#000000"; red = "#ff5555"; green = "#50fa7b"; yellow = "#f1fa8c"; blue = "#bd93f9"; magenta = "#ff79c6"; cyan = "#8be9fd"; white = "#bfbfbf"; };
        bright = { black = "#555555"; red = "#ff6e67"; green = "#5af78e"; yellow = "#f4f99d"; blue = "#caa9fa"; magenta = "#ff92d0"; cyan = "#9aedfe"; white = "#ffffff"; };
      };
    }; 
  };
  
  home.packages = with pkgs; [ bat
  python3
  python3Packages.requests
  (writeShellScriptBin "wimbledon-scores-launcher" ''
    #!${pkgs.stdenv.shell}
    ${pkgs.python3.withPackages (ps: [ ps.requests ])}/bin/python3 ${config.home.homeDirectory}/.config/qtile/scripts/wimbledon_scores.py "$@"
  '')
  (writeShellScriptBin "soccer-scores-launcher" ''
    #!${pkgs.stdenv.shell}
    ${pkgs.python3.withPackages (ps: [ ps.requests ])}/bin/python3 ${config.home.homeDirectory}/.config/qtile/scripts/soccer_scores.py "$@"
  '')
 ];
  fonts.fontconfig.enable = true;
}

