--core settings
vim.opt.splitbelow = true
vim.opt.scrolloff = 999
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.termguicolors = true
vim.opt.signcolumn = "yes"
vim.opt.updatetime = 300
vim.opt.cursorline = true
vim.opt.expandtab = true
vim.opt.shiftwidth = 2
vim.opt.tabstop = 2
vim.g.mapleader = " "

--imports
require("plugins")
require("remaps")
require("lsp")
