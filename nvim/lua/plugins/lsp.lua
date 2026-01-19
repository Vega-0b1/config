return {
	"neovim/nvim-lspconfig",
	dependencies = {
		{ "mason-org/mason.nvim", config = true },
		"mason-org/mason-lspconfig.nvim",
	},
	config = function()
		require("mason-lspconfig").setup({
			ensure_installed = {
				"lua_ls",
				"pyright",
				"jdtls",
				"rust_analyzer",
				"jsonls",
				"html",
				"cssls",
				"clangd",
				"ts_ls",
			},
		})

		-- Neovim 0.11+
		if vim.lsp.config then
			vim.lsp.config("lua_ls", { settings = { Lua = { diagnostics = { globals = { "vim" } } } } })
			return
		end

		-- Neovim 0.10 and older
		require("lspconfig").lua_ls.setup({
			settings = { Lua = { diagnostics = { globals = { "vim" } } } },
		})
	end,
}
