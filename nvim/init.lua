-- Core settings
vim.opt.scrolloff = 999
vim.o.number = true
vim.o.relativenumber = true
vim.o.termguicolors = true
vim.o.signcolumn = "yes"
vim.o.updatetime = 300
vim.o.cursorline = true
vim.o.expandtab = true
vim.o.shiftwidth = 2
vim.o.tabstop = 2
vim.g.mapleader = " "

-- Load other config modules
require("remaps")
require("plugins")
require("cmp")
require("lsp")
require("lualine").setup()

local null_ls = require("null-ls")

null_ls.setup({
	sources = {
		null_ls.builtins.formatting.stylua,
		null_ls.builtins.completion.spell,
		null_ls.builtins.formatting.clang_format,
		null_ls.builtins.diagnostics.cppcheck,
		require("none-ls.diagnostics.eslint"), -- requires none-ls-extras.nvim
	},
})
