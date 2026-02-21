-- lua/plugins/lsp.lua
return {
	{
		"neovim/nvim-lspconfig",
		config = function()
			local capabilities = require('blink.cmp').get_lsp_capabilities(vim.lsp.protocol.make_client_capabilities())

			-- Define configs (Neovim 0.11+ + lspconfig new API)
			vim.lsp.config("rust_analyzer", {
				capabilities = capabilities,
			})
			vim.lsp.enable("rust_analyzer")

			vim.lsp.config("pyright", {
				capabilities = capabilities,
			})
			vim.lsp.enable("pyright")

			-- Java: jdtls often requires a dedicated launcher (workspace/cmd).
			-- This enables it if your setup starts it correctly.
			vim.lsp.config("jdtls", {
				capabilities = capabilities,
			})
			vim.lsp.enable("jdtls")

			vim.lsp.config("clangd", {
				capabilities = capabilities,
			})
			vim.lsp.enable("clangd")

			-- JS/TS: lspconfig renamed tsserver -> ts_ls
			vim.lsp.config("ts_ls", {
				capabilities = capabilities,
			})
			vim.lsp.enable("ts_ls")

			vim.lsp.config("html", {
				capabilities = capabilities,
			})
			vim.lsp.enable("html")

			vim.lsp.config("cssls", {
				capabilities = capabilities,
			})
			vim.lsp.enable("cssls")

			vim.lsp.config("lua_ls", {
				capabilities = capabilities,
				settings = {
					Lua = {
						diagnostics = { globals = { "vim" } },
						workspace = { checkThirdParty = false },
						telemetry = { enable = false },
					},
				},
			})
			vim.lsp.enable("lua_ls")
		end,
	},
}
