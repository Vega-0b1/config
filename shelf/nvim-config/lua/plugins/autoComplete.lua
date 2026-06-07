return {
	"saghen/blink.cmp",
	version = "1.*",
	opts = {
		keymap = { preset = "super-tab" },
		sources = {
			providers = {
				lsp      = { min_keyword_length = 5 },
				buffer   = { min_keyword_length = 5 },
				snippets = { min_keyword_length = 5 },
				path     = { min_keyword_length = 5 },
			},
		},
		completion = {
			menu = { auto_show = false },
			documentation = { auto_show = false },
			ghost_text = { enabled = true, show_with_menu = false, show_without_selection = true },
		},
	},
}
