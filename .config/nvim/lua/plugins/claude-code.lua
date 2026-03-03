return {
	"greggh/claude-code.nvim",
	dependencies = { "nvim-lua/plenary.nvim" },
	config = function()
		require("claude-code").setup({
			window = {
				split_ratio = 0.4,
				position = "vertical botright",
			},
			git = {
				use_git_root = false,
			},
			keymaps = {
				toggle = {
					normal = "<leader>c",
					terminal = "<Esc>",
					variants = {
						continue = "<leader>cc",
						verbose = "<leader>cv",
					},
				},
				window_navigation = true,
				scrolling = true,
			},
		})
	end,
}
