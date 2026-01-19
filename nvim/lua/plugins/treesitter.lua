return {
	"nvim-treesitter/nvim-treesitter",
	lazy = false,
	build = ":TSUpdate",
	config = function()
		require("nvim-treesitter").setup({})

		require("nvim-treesitter").install({
			"lua",
			"python",
			"java",
			"rust",
			"json",
			"html",
			"css",
			"javascript",
			"typescript",
			"tsx",
		})
	end,
}
