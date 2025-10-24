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

require("lazy").setup({
	-- UI
  
 {
    "rebelot/kanagawa.nvim",
    priority = 1000,
    lazy = false,
    config = function()
      vim.o.termguicolors = true
      -- pick one:
      vim.cmd.colorscheme("kanagawa-wave")   -- dark

      vim.cmd("hi Normal guibg=#000000 ctermbg=black")
      --vim.cmd.colorscheme("kanagawa-dragon") -- darker
      --vim.cmd.colorscheme("kanagawa-lotus")     -- light
    end,
  },
	{
		"akinsho/toggleterm.nvim",
		version = "*",
		config = function()
			local toggleterm = require("toggleterm")

			toggleterm.setup({
				open_mapping = [[<c-\>]],
				direction = "float", -- or "horizontal", "vertical", "tab"
				shade_terminals = true,
			})

			-- Create a terminal instance
			local Terminal = require("toggleterm.terminal").Terminal
			local my_terminal = Terminal:new({ hidden = true })

			-- Keymap to toggle that terminal
			vim.keymap.set("n", "<leader>tt", function()
				my_terminal:toggle()
			end, { desc = "Toggle Terminal" })
		end,
	},
	-- Comment toggling
	{
		"numToStr/Comment.nvim",
		config = function()
			require("Comment").setup()
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
	{ "rebelot/kanagawa.nvim" },
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
				},
				automatic_installation = true,
				automatic_enable = true,
			})
		end,
	},

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

	-- Formatter/Linter
	{ "nvimtools/none-ls.nvim" },

	-- Treesitter
	{
		"nvim-treesitter/nvim-treesitter",
		build = ":TSUpdate",
		config = function()
			require("nvim-treesitter.configs").setup({
				ensure_installed = { "lua", "python", "json", "bash", "javascript", "typescript", "rust" },
				highlight = { enable = true },
				indent = { enable = true },
			})
		end,
	},

	-- Telescope
	{
		"nvim-telescope/telescope.nvim",
		dependencies = { "nvim-lua/plenary.nvim" },
		config = true,
	},

	-- File Explorer
	{
		"stevearc/oil.nvim",
		config = function()
			require("oil").setup()
		end,
	},
})
