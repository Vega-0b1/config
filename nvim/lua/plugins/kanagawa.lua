return {
	"rebelot/kanagawa.nvim",
	priority = 1000,
	lazy = false,
	config = function()
		vim.o.termguicolors = true
		vim.cmd.colorscheme("kanagawa-wave") -- dark --
	end,
}
