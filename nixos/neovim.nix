# ~/dotfiles/nixos/neovim.nix
#
# This file contains the declarative configuration for Neovim.

{ config, pkgs, ... }:

{
  programs.neovim = {
    enable = true;
    defaultEditor = true; # Make nvim the default 'vi' and 'editor'
    
    # This section configures Neovim plugins using lazy.nvim
    plugins = with pkgs.vimPlugins; [
      # Plugin Manager
      lazy-nvim

      # A solid foundation for LSP, completion, and formatting
      lsp-zero-nvim

      # Dependencies for lsp-zero
      mason-nvim
      mason-lspconfig-nvim
      nvim-lspconfig
      nvim-cmp
      cmp-nvim-lsp
      luasnip

      # Syntax highlighting
      nvim-treesitter.withAllGrammars

      # File browsing and fuzzy finding
      telescope-nvim
      plenary-nvim # A dependency for telescope

      # A beautiful theme that matches your desktop
      catppuccin-nvim
    ];

    # This is where you configure the plugins
    extraLuaConfig = ''
      -- Set the theme
      vim.cmd.colorscheme "catppuccin"

      -- Configure lsp-zero
      local lsp_zero = require('lsp-zero')
      lsp_zero.on_attach(function(client, bufnr)
        lsp_zero.default_keymaps({buffer = bufnr})
      end)

      -- Setup mason to manage LSPs
      require('mason').setup({})
      require('mason-lspconfig').setup({
        ensure_installed = {
          'tsserver', -- For TypeScript/JavaScript
          'html',
          'cssls',
          'emmet_ls', -- For HTML/CSS abbreviations
        },
        handlers = {
          lsp_zero.default_setup,
        },
      })
      
      -- Basic options
      vim.opt.number = true
      vim.opt.relativenumber = true
      vim.opt.termguicolors = true
    '';
  };
}

