return {
	"saghen/blink.cmp",
	version = "1.*",
	opts = {
		keymap = { preset = "super-tab" },
		sources = {
			min_keyword_length = 3, -- start suggesting after 3 chars :contentReference[oaicite:1]{index=1}
		},
		completion = {
			menu = { auto_show = false },
			documentation = { auto_show = false },
			ghost_text = { enabled = true, show_with_menu = false, show_without_selection = true },
		},
	},
}
