return {
	"rebelot/kanagawa.nvim",
	priority = 1000,
	lazy = false,
	config = function()
		require("kanagawa").setup({
			transparent = true,
			colors = {
				theme = { all = { ui = { bg_gutter = "none" } } },
			},
			overrides = function(colors)
				local d = colors.theme.diag
				local bg = colors.theme.ui.bg
				local c = require("kanagawa.lib.color")
				local function mute(color)
					return c(color):blend(bg, 0.7):to_hex()
				end
				return {
					DiagnosticVirtualTextError = { link = "Comment" },
					DiagnosticVirtualTextWarn  = { link = "Comment" },
					DiagnosticVirtualTextInfo  = { link = "Comment" },
					DiagnosticVirtualTextHint  = { link = "Comment" },
					DiagnosticSignError        = { fg = mute(d.error) },
					DiagnosticSignWarn         = { fg = mute(d.warning) },
					DiagnosticSignInfo         = { fg = mute(d.info) },
					DiagnosticSignHint         = { fg = mute(d.hint) },
				}
			end,
		})
		vim.cmd.colorscheme("kanagawa-wave") -- dark --
	end,
}
