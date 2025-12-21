--check if lazy.nvim is installed if not it installs it

local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
	vim.fn.system({
		"git",
		"clone",
		"--filter=blob:none",
		"https://github.com/folke/lazy.nvim.git",
		lazypath,
	})
end
vim.opt.rtp:prepend(lazypath)

-----------------------------------------------plugin wrapper start---------------------------------------
require("lazy").setup({

	{
		"rebelot/kanagawa.nvim",
		priority = 1000,
		lazy = false,
		config = function()
			vim.o.termguicolors = true
			-- pick one:
			vim.cmd.colorscheme("kanagawa-wave") -- dark

			--vim.cmd.colorscheme("kanagawa-dragon") -- darker
			--vim.cmd.colorscheme("kanagawa-lotus")     -- light
		end,
	},

	-- Autopairs
	{
		"windwp/nvim-autopairs",
		event = "InsertEnter",
		config = function()
			require("nvim-autopairs").setup()
		end,
	},

	-- Indent guides
	{
		"lukas-reineke/indent-blankline.nvim",
		main = "ibl",
		opts = {},
	},

	{ "nvim-lualine/lualine.nvim", config = true },

	-- LSP
	{ "neovim/nvim-lspconfig" },
	{ "williamboman/mason.nvim", build = ":MasonUpdate", config = true },
	{
		"williamboman/mason-lspconfig.nvim",
		dependencies = {
			"neovim/nvim-lspconfig",
			"hrsh7th/cmp-nvim-lsp",
		},
		config = function()
			require("mason").setup()
			require("mason-lspconfig").setup({
				ensure_installed = {
					"clangd",
					"lua_ls",
					"ts_ls",
					"pyright",
					"bashls",
					"rust_analyzer",
					"jdtls",
				},
				automatic_installation = true,
				automatic_enable = true,
			})
		end,
	},
	{ "mfussenegger/nvim-jdtls" },
	-- Autocomplete

	{
		"hrsh7th/nvim-cmp",
		config = function()
			local cmp = require("cmp")
			cmp.setup({
				mapping = cmp.mapping.preset.insert({
					["<Tab>"] = cmp.mapping.select_next_item(),
					["<S-Tab>"] = cmp.mapping.select_prev_item(),
					["<CR>"] = cmp.mapping.confirm({ select = true }),
				}),
				sources = {
					{ name = "nvim_lsp" },
				},
			})
		end,
	},
	{ "hrsh7th/cmp-nvim-lsp" },

	-- Treesitter
	{
		"nvim-treesitter/nvim-treesitter",
		build = ":TSUpdate",
		config = function()
			require("nvim-treesitter.configs").setup({
				ensure_installed = { "lua", "python", "json", "bash", "javascript", "typescript", "rust", "java" },
				highlight = { enable = true },
				indent = { enable = true },
			})
		end,
	},

	-- Telescope

	{
		"nvim-telescope/telescope.nvim",
		dependencies = { "nvim-lua/plenary.nvim" },
		config = function()
			local builtin = require("telescope.builtin")

			vim.keymap.set("n", "<leader>ff", builtin.find_files, { desc = "Find files" })
			vim.keymap.set("n", "<leader>fg", builtin.live_grep, { desc = "Live grep" })
			vim.keymap.set("n", "<leader>fb", builtin.buffers, { desc = "Buffers" })
			vim.keymap.set("n", "<leader>fh", builtin.help_tags, { desc = "Help tags" })
		end,
	},
	{
		"nvimtools/none-ls.nvim",
		dependencies = {
			"nvimtools/none-ls-extras.nvim",
		},
	},
})
