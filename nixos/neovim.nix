# ~/dotfiles/nixos/neovim.nix
#
# This file contains the declarative configuration for Neovim.
# This version removes the deprecated 'lsp-zero' and uses a standard LSP setup.

{ config, pkgs, ... }:

{
  programs.neovim = {
    enable = true;
    defaultEditor = true;
    
    # We keep most of the same plugins, just removing lsp-zero
    plugins = with pkgs.vimPlugins; [
      lazy-nvim
      mason-nvim
      mason-lspconfig-nvim
      nvim-lspconfig
      nvim-cmp
      cmp-nvim-lsp
      luasnip
      cmp_luasnip
      nvim-treesitter.withAllGrammars
      telescope-nvim
      plenary-nvim
      catppuccin-nvim
    ];

    # This Lua configuration now sets up the plugins directly
    extraLuaConfig = ''
      -- Set theme
      vim.cmd.colorscheme "catppuccin"

      -- Basic editor options
      vim.opt.number = true
      vim.opt.relativenumber = true
      vim.opt.termguicolors = true
      vim.opt.mouse = 'a'
      vim.opt.expandtab = true
      vim.opt.shiftwidth = 2
      vim.opt.tabstop = 2

      -- Setup Mason to manage Language Servers
      require("mason").setup()
      require("mason-lspconfig").setup({
        ensure_installed = { "tsserver", "html", "cssls", "emmet_ls" },
      })

      -- Setup nvim-cmp (autocompletion)
      local cmp = require('cmp')
      cmp.setup({
        snippet = {
          expand = function(args)
            require('luasnip').lsp_expand(args.body)
          end,
        },
        sources = cmp.config.sources({
          { name = 'nvim_lsp' },
          { name = 'luasnip' },
        }),
        mapping = cmp.mapping.preset.insert({
          ['<C-b>'] = cmp.mapping.scroll_docs(-4),
          ['<C-f>'] = cmp.mapping.scroll_docs(4),
          ['<C-Space>'] = cmp.mapping.complete(),
          ['<C-e>'] = cmp.mapping.abort(),
          ['<CR>'] = cmp.mapping.confirm({ select = true }),
        }),
      })

      -- Setup nvim-lspconfig
      local lspconfig = require('lspconfig')
      local capabilities = require('cmp_nvim_lsp').default_capabilities()

      -- Loop through servers installed by Mason and attach them
      for _, server in ipairs(require("mason-lspconfig").get_installed_servers()) do
        lspconfig[server].setup({
          capabilities = capabilities,
        })
      end
    '';
  };
}

