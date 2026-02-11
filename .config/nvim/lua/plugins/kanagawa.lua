return {
	"rebelot/kanagawa.nvim",
	priority = 1000,
	lazy = false,
	config = function()
		vim.o.termguicolors = true
		require("kanagawa").setup({
			transparent = true,
			colors = {
				them = { all = { ui = { bg_gutter = "none" } } },
			},
		})
		vim.cmd.colorscheme("kanagawa-wave") -- dark --
	end,
}
