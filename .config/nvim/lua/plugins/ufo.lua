-- Custom treesitter provider using treesitter fold queries directly
-- (ufo's built-in treesitter provider is incompatible with newer nvim-treesitter)
local function ts_folds(bufnr)
	local ok, parser = pcall(vim.treesitter.get_parser, bufnr)
	if not ok or not parser then return {} end

	local trees = parser:parse()
	if not trees or #trees == 0 then return {} end

	local lang = parser:lang()
	local ok2, query = pcall(vim.treesitter.query.get, lang, "folds")
	if not ok2 or not query then return {} end

	local folds = {}
	for _, tree in ipairs(trees) do
		for _, node in query:iter_captures(tree:root(), bufnr) do
			local start_row, _, end_row, end_col = node:range()
			if end_col == 0 then end_row = end_row - 1 end
			if end_row > start_row then
				table.insert(folds, { startLine = start_row, endLine = end_row })
			end
		end
	end
	return folds
end

return {
	"kevinhwang91/nvim-ufo",
	dependencies = { "kevinhwang91/promise-async" },
	config = function()
		require("ufo").setup({
			provider_selector = function()
				return { "lsp", ts_folds }
			end,
		})

		vim.keymap.set("n", "zR", require("ufo").openAllFolds)
		vim.keymap.set("n", "zM", require("ufo").closeAllFolds)

		-- K: peek fold if one exists, otherwise fall through to LSP hover
		vim.keymap.set("n", "K", function()
			local winid = require("ufo").peekFoldedLinesUnderCursor()
			if not winid then
				vim.lsp.buf.hover()
			end
		end)
	end,
}
