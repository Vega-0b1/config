
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
	vim.fn.system({
		"git",
		"clone",
		"--filter=blob:none",
		"https://github.com/folke/lazy.nvim.git",
		lazypath,
	})
end
vim.opt.rtp:prepend(lazypath)

-----------------------------------------------plugin wrapper start---------------------------------------
require("lazy").setup({

{ "rebelot/kanagawa.nvim", 
  priority = 1000, lazy = false, 
  config = function() vim.o.termguicolors = true 
     vim.cmd.colorscheme("kanagawa-wave") -- dark --
    end, },

	-- Indent guides
	{
		"lukas-reineke/indent-blankline.nvim",
		main = "ibl",
		opts = {},
	},

	-- Telescope
	{
		"nvim-telescope/telescope.nvim",
		dependencies = { "nvim-lua/plenary.nvim" },
		config = function()
			local builtin = require("telescope.builtin")

		end,
	},


{
  "stevearc/conform.nvim",
  event = { "BufWritePre" },
  cmd = { "ConformInfo" },
  opts = {
    formatters_by_ft = {
      -- Web / config
      javascript = { "prettier" },
      typescript = { "prettier" },
      javascriptreact = { "prettier" },
      typescriptreact = { "prettier" },
      json = { "prettier" },
      jsonc = { "prettier" },
      yaml = { "prettier" },
      html = { "prettier" },
      css = { "prettier" },
      markdown = { "prettier" },

      -- Systems languages
      c = { "clang-format" },
      cpp = { "clang-format" },
      rust = { "rustfmt" },
      go = { "gofmt" },

      -- Scripting
      python = { "black" },
      lua = { "stylua" },

      -- Shell
      sh = { "shfmt" },
      bash = { "shfmt" },
      zsh = { "shfmt" },

      -- Java
      java = { "google-java-format" },
    },

    format_on_save = { timeout_ms = 1000, lsp_fallback = true },
  },
}
 --end 
})
