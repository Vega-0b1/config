--core settings

vim.opt.shortmess:append("I")
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

vim.api.nvim_create_autocmd("FileType", {
	pattern = { "lua", "python", "java", "rust", "json", "html", "css", "javascript", "typescript", "tsx" },
	callback = function()
		vim.treesitter.start()
	end,
})
vim.diagnostic.config({
	virtual_text = true,
})

--plugins
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

require("lazy").setup({
	{ import = "plugins" },
})

--remaps
require("remaps")
