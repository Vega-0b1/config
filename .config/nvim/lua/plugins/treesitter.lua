return {
	"nvim-treesitter/nvim-treesitter",
	lazy = false,
	build = ":TSUpdate",
	config = function()
		-- Modern nvim-treesitter has simplified API
		-- setup() is optional and only needed for custom install_dir
		require("nvim-treesitter").setup({})

		-- Install parsers (runs async, only installs if missing)
		local parsers = {
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
			"bash",
			"regex",
		}

		-- Check which parsers are missing before installing
		local installed = require("nvim-treesitter").get_installed()
		local to_install = {}
		for _, parser in ipairs(parsers) do
			if not vim.tbl_contains(installed, parser) then
				table.insert(to_install, parser)
			end
		end

		if #to_install > 0 then
			require("nvim-treesitter").install(to_install)
		end
	end,
}
