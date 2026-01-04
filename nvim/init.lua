-- Core settings
vim.opt.splitbelow = true
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
require("lsp")

