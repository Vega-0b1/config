return {
	"windwp/nvim-ts-autotag",
	event = { "BufReadPre", "BufNewFile" },
	config = function()
		require("nvim-ts-autotag").setup({
			opts = {
				enable_close = true, -- auto-close tags
				enable_rename = true, -- auto-rename paired tags
				enable_close_on_slash = false,
			},
			-- Optional: restrict to certain filetypes
			-- filetypes = { "html", "xml", "javascriptreact", "typescriptreact", "tsx", "jsx" },
		})
	end,
}
