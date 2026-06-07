return {
	"mfussenegger/nvim-lint",
	event = { "BufReadPre", "BufNewFile" },
	config = function()
		local lint = require("lint")

		lint.linters_by_ft = {
			-- JS/TS
			javascript = { "eslint_d" },
			typescript = { "eslint_d" },
			javascriptreact = { "eslint_d" },
			typescriptreact = { "eslint_d" },

			-- HTML
			html = { "htmlhint" },
		}

		-- If eslint_d isn't available, fall back to eslint (if installed)
		vim.api.nvim_create_autocmd("FileType", {
			pattern = { "javascript", "typescript", "javascriptreact", "typescriptreact" },
			callback = function()
				if vim.fn.executable("eslint_d") == 0 and vim.fn.executable("eslint") == 1 then
					lint.linters_by_ft[vim.bo.filetype] = { "eslint" }
				end
			end,
		})

		local grp = vim.api.nvim_create_augroup("nvim_lint", { clear = true })

		vim.api.nvim_create_autocmd({ "BufEnter", "BufWritePost", "InsertLeave" }, {
			group = grp,
			callback = function()
				lint.try_lint()
			end,
		})

		vim.keymap.set("n", "<leader>l", function()
			lint.try_lint()
		end, { desc = "Lint file" })
	end,
}
