{config, pkgs, ...}:
 
{
  imports = [ ./neovim.nix ];

 home.username = "balint";
  home.homeDirectory = "/home/balint";
  home.stateVersion = "24.05";

  # --- Your Personal Settings ---
  programs.bash = {
    enable =  true;
    shellAliases = {
      btw = "echo nixos";
nrs = "cd ~/dotfiles && sudo nixos-rebuild switch --flake .#nixos";
nix = "sudo -E nvim /etc/nixos/configuration.nix";
pnix = "sudo -E nvim /etc/nixos/packages.nix";
snix = "sudo -E nvim /etc/nixos/system.nix";
      qtile = "sudo -E nvim ~/.config/qtile/config.py";
      homenix= "sudo -E nvim /etc/nixos/home.nix";
    };
  };

  programs.alacritty = {
    enable = true;
    settings = {
      # Window Settings
      window = {
        padding = { x = 10; y = 10; };
        opacity = 0.95; # Slightly adjusted for better text clarity
      };

      # Font Configuration
      font = {
        normal = {
          family = "FiraCode Nerd Font";
          style = "Regular";
        };
        bold = {
          family = "FiraCode Nerd Font";
          style = "Bold";
        };
        italic = {
          family = "FiraCode Nerd Font";
          style = "Italic";
        };
        size = 12;
      };

      # Cursor Style
      cursor = {
        style = {
          shape = "Block";
          blinking = "On";
        };
      };
      
      # Dracula Color Scheme (to match your Qtile config)
      colors = {
        primary = {
          background = "#282a36";
          foreground = "#f8f8f2";
        };
        cursor = {
          text = "#282a36";
          cursor = "#f8f8f2";
        };
        selection = {
          text = "#f8f8f2";
          background = "#44475a";
        };
        normal = {
          black = "#000000";
          red = "#ff5555";
          green = "#50fa7b";
          yellow = "#f1fa8c";
          blue = "#bd93f9";
          magenta = "#ff79c6";
          cyan = "#8be9fd";
          white = "#bfbfbf";
        };
        bright = {
          black = "#555555";
          red = "#ff6e67";
          green = "#5af78e";
          yellow = "#f4f99d";
          blue = "#caa9fa";
          magenta = "#ff92d0";
          cyan = "#9aedfe";
          white = "#ffffff";
        };
      };
    }; 
  };
  home.packages = with pkgs; [ bat ];
  fonts.fontconfig.enable = true;
}

