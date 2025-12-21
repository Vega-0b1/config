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

-- Rust: format on save via rust-analyzer (which runs rustfmt)
local aug_rust = vim.api.nvim_create_augroup("RustFormatOnSave", { clear = true })

vim.api.nvim_create_autocmd("BufWritePre", {
	group = aug_rust,
	pattern = { "*.rs" },
	callback = function(args)
		vim.lsp.buf.format({
			timeout_ms = 1500,
			bufnr = args.buf,
			filter = function(client)
				-- use rust-analyzer, not null-ls
				return client.name == "rust_analyzer"
			end,
		})
	end,
})

-- Java: format on save via null-ls (google-java-format)
local aug_java = vim.api.nvim_create_augroup("JavaFormatOnSave", { clear = true })

vim.api.nvim_create_autocmd("BufWritePre", {
	group = aug_java,
	pattern = { "*.java" },
	callback = function(args)
		vim.lsp.buf.format({
			timeout_ms = 1500,
			bufnr = args.buf,
			filter = function(client)
				return client.name == "null-ls"
			end,
		})
	end,
})
