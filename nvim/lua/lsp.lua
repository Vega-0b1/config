local aug_cpp = vim.api.nvim_create_augroup("CppFormatOnSave", { clear = true })

vim.api.nvim_create_autocmd("BufWritePre", {
	group = aug_cpp,
	pattern = { "*.c", "*.h", "*.cpp", "*.hpp", "*.cc", "*.cxx" },
	callback = function()
		vim.lsp.buf.format({
			timeout_ms = 1500,
			filter = function(client)
				return client.name == "null-ls" -- use clang-format
			end,
		})
	end,
})

-- Format Lua files on save

local aug_lua = vim.api.nvim_create_augroup("FormatLuaOnSave", {})

vim.api.nvim_create_autocmd("BufWritePre", {
	group = aug_lua,
	pattern = { "*.lua", "*.luau" },
	callback = function()
		vim.lsp.buf.format({
			timeout_ms = 1500,
			filter = function(client)
				return client.name == "null-ls"
			end,
		})
	end,
})
