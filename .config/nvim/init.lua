vim.g.mapleader = " "

vim.opt.shortmess:append("I")
vim.opt.modeline = false
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
vim.opt.undofile = true
vim.opt.undodir = vim.fn.stdpath("data") .. "/undo"

vim.diagnostic.config({
  virtual_text = {
    spacing = 4,
    prefix = "·",
  },
})

-- Bootstrap lazy.nvim
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup("plugins")
require("remaps")
