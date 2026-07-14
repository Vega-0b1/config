return {

  -- Dracula colorscheme
  {
    "Mofiqul/dracula.nvim",
    config = function()
      require("dracula").setup({ transparent_bg = true })
    end,
  },

  -- Rose Pine colorscheme (primary) with Alacritty theme sync
  {
    "rose-pine/neovim",
    name = "rose-pine",
    priority = 1000,
    config = function()
      local _states = {
        { variant = "main", transparent = true },
        { variant = "dawn", transparent = true },
      }
      local _state = 1

      local function rosepine_apply(state)
        require("rose-pine").setup({
          variant = state.variant,
          styles = { transparency = state.transparent },
          highlight_groups = {
            DiagnosticVirtualTextError = { link = "Comment" },
            DiagnosticVirtualTextWarn  = { link = "Comment" },
            DiagnosticVirtualTextInfo  = { link = "Comment" },
            DiagnosticVirtualTextHint  = { link = "Comment" },
            RainbowDelimiterRed    = { fg = "love" },
            RainbowDelimiterYellow = { fg = "gold" },
            RainbowDelimiterBlue   = { fg = "foam" },
            RainbowDelimiterOrange = { fg = "rose" },
            RainbowDelimiterGreen  = { fg = "pine" },
            RainbowDelimiterViolet = { fg = "iris" },
            RainbowDelimiterCyan   = { fg = "foam" },
          },
        })
        vim.cmd.colorscheme("rose-pine")
      end

      local function write_alacritty(toml)
        local path = vim.fn.expand("~/.config/alacritty/theme.toml")
        vim.fn.writefile(vim.split(toml, "\n"), path)
      end

      local main_toml = [[
[window]
opacity = 0.97

[colors.primary]
background = '#191724'
foreground = '#e0def4'

[colors.normal]
black = '#26233a'
red = '#eb6f92'
green = '#31748f'
yellow = '#f6c177'
blue = '#9ccfd8'
magenta = '#c4a7e7'
cyan = '#ebbcba'
white = '#e0def4'

[colors.bright]
black = '#6e6a86'
red = '#eb6f92'
green = '#31748f'
yellow = '#f6c177'
blue = '#9ccfd8'
magenta = '#c4a7e7'
cyan = '#ebbcba'
white = '#e0def4'
]]

      local dawn_toml = [[
[window]
opacity = 0.97

[colors.primary]
background = '#faf4ed'
foreground = '#575279'

[colors.normal]
black = '#f2e9e1'
red = '#b4637a'
green = '#286983'
yellow = '#ea9d34'
blue = '#56949f'
magenta = '#907aa9'
cyan = '#d7827e'
white = '#575279'

[colors.bright]
black = '#9893a5'
red = '#b4637a'
green = '#286983'
yellow = '#ea9d34'
blue = '#56949f'
magenta = '#907aa9'
cyan = '#d7827e'
white = '#575279'
]]

      local _alacritty_themes = { main_toml, dawn_toml }

      rosepine_apply(_states[_state])
      write_alacritty(_alacritty_themes[_state])

      _G._theme_cycle = function()
        _state = (_state % #_states) + 1
        rosepine_apply(_states[_state])
        write_alacritty(_alacritty_themes[_state])
      end
    end,
  },

  -- Completion (before lspconfig so capabilities are available)
  {
    "Saghen/blink.cmp",
    version = "*",
    config = function()
      require("blink.cmp").setup({
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
          menu          = { auto_show = false },
          documentation = { auto_show = false },
          ghost_text    = { enabled = true, show_with_menu = false, show_without_selection = true },
        },
      })
    end,
  },

  -- LSP
  {
    "neovim/nvim-lspconfig",
    dependencies = { "Saghen/blink.cmp" },
    config = function()
      local capabilities = require("blink.cmp").get_lsp_capabilities(
        vim.lsp.protocol.make_client_capabilities()
      )

      vim.lsp.config('*', { capabilities = capabilities })

      vim.lsp.enable("rust_analyzer")
      vim.lsp.enable("pyright")
      vim.lsp.enable("jdtls")

      vim.lsp.config("clangd", {
        cmd = { "clangd", "--function-arg-placeholders=false" },
      })
      vim.lsp.enable("clangd")

      vim.lsp.enable("ts_ls")
      vim.lsp.enable("html")
      vim.lsp.enable("cssls")

      vim.lsp.config("lua_ls", {
        settings = {
          Lua = {
            diagnostics = { globals = { "vim" } },
            workspace   = { checkThirdParty = false },
            telemetry   = { enable = false },
          },
        },
      })
      vim.lsp.enable("lua_ls")

      vim.lsp.enable("bashls")
      vim.lsp.enable("kotlin_language_server")
    end,
  },

  -- Treesitter
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    config = function()
      require("nvim-treesitter.configs").setup({
        ensure_installed = {
          "lua", "python", "java", "rust", "json",
          "html", "css", "javascript", "typescript", "tsx",
          "bash", "regex", "c", "cpp", "nix", "kotlin",
        },
        highlight = { enable = true },
        indent    = { enable = true },
      })
    end,
  },

  -- Auto-close HTML/JSX tags
  {
    "windwp/nvim-ts-autotag",
    dependencies = { "nvim-treesitter/nvim-treesitter" },
    config = function()
      require("nvim-ts-autotag").setup({
        opts = {
          enable_close          = true,
          enable_rename         = true,
          enable_close_on_slash = false,
        },
      })
    end,
  },

  -- Telescope fuzzy finder
  { "nvim-lua/plenary.nvim" },
  {
    "nvim-telescope/telescope.nvim",
    dependencies = { "nvim-lua/plenary.nvim" },
    config = function()
      -- keybinds in remaps.lua
    end,
  },

  -- Formatting
  {
    "stevearc/conform.nvim",
    config = function()
      require("conform").setup({
        formatters_by_ft = {
          javascript      = { "prettier" },
          typescript      = { "prettier" },
          javascriptreact = { "prettier" },
          typescriptreact = { "prettier" },
          json            = { "prettier" },
          jsonc           = { "prettier" },
          yaml            = { "prettier" },
          html            = { "prettier" },
          css             = { "prettier" },
          markdown        = { "prettier" },
          c               = { "clang-format" },
          cpp             = { "clang-format" },
          rust            = { "rustfmt" },
          python          = { "black" },
          lua             = { "stylua" },
          sh              = { "shfmt" },
          bash            = { "shfmt" },
          zsh             = { "shfmt" },
          java            = { "google-java-format" },
        },
        format_on_save = { timeout_ms = 1000, lsp_format = "fallback" },
      })
    end,
  },

  -- Linting
  {
    "mfussenegger/nvim-lint",
    config = function()
      local lint = require("lint")
      lint.linters_by_ft = {
        javascript      = { "eslint_d" },
        typescript      = { "eslint_d" },
        javascriptreact = { "eslint_d" },
        typescriptreact = { "eslint_d" },
        html            = { "htmlhint" },
      }

      vim.api.nvim_create_autocmd("FileType", {
        pattern  = { "javascript", "typescript", "javascriptreact", "typescriptreact" },
        callback = function()
          if vim.fn.executable("eslint_d") == 0 and vim.fn.executable("eslint") == 1 then
            lint.linters_by_ft[vim.bo.filetype] = { "eslint" }
          end
        end,
      })

      local grp = vim.api.nvim_create_augroup("nvim_lint", { clear = true })
      vim.api.nvim_create_autocmd({ "BufEnter", "BufWritePost", "InsertLeave" }, {
        group    = grp,
        callback = function() lint.try_lint() end,
      })

      vim.keymap.set("n", "<leader>l", function() lint.try_lint() end, { desc = "Lint file" })
    end,
  },

  -- UI: notifications
  { "MunifTanjim/nui.nvim" },
  {
    "rcarriga/nvim-notify",
    config = function()
      require("notify").setup({
        stages  = "static",
        timeout = 800,
      })
    end,
  },

  -- UI: command palette / prettier cmdline
  {
    "folke/noice.nvim",
    dependencies = { "MunifTanjim/nui.nvim", "rcarriga/nvim-notify" },
    config = function()
      require("noice").setup({
        lsp = {
          progress = { enabled = false },
          override = {
            ["vim.lsp.util.convert_input_to_markdown_lines"] = true,
            ["vim.lsp.util.stylize_markdown"]                = true,
          },
        },
        presets = {
          bottom_search         = true,
          command_palette       = true,
          long_message_to_split = true,
          inc_rename            = false,
          lsp_doc_border        = false,
        },
        views = {
          notify = { timeout = 1500 },
          mini   = { timeout = 1500 },
        },
      })
    end,
  },

  -- UI: indent guides
  {
    "lukas-reineke/indent-blankline.nvim",
    main = "ibl",
    config = function()
      require("ibl").setup()
    end,
  },

  -- UI: rainbow bracket colors (colors managed by rose-pine highlight_groups)
  { "HiPhish/rainbow-delimiters.nvim" },

  -- UI: scroll past EOF
  {
    "Aasim-A/scrollEOF.nvim",
    config = function()
      require("scrollEOF").setup()
    end,
  },

  -- UI: auto-pair brackets
  {
    "windwp/nvim-autopairs",
    config = function()
      local ap = require("nvim-autopairs")
      local Rule = require("nvim-autopairs.rule")
      ap.setup({ check_ts = true })
      ap.clear_rules()
      ap.add_rule(Rule("{", "}"):with_move(function() return true end))
    end,
  },

  -- Navigation: harpoon2
  {
    "ThePrimeagen/harpoon",
    branch = "harpoon2",
    dependencies = { "nvim-lua/plenary.nvim" },
    config = function()
      local harpoon = require("harpoon")
      harpoon:setup({})

      local conf = require("telescope.config").values
      local function toggle_telescope(harpoon_files)
        local file_paths = {}
        for _, item in ipairs(harpoon_files.items) do
          table.insert(file_paths, item.value)
        end
        require("telescope.pickers").new({}, {
          prompt_title = "Harpoon",
          finder       = require("telescope.finders").new_table({ results = file_paths }),
          previewer    = conf.file_previewer({}),
          sorter       = conf.generic_sorter({}),
        }):find()
      end

      local map = vim.keymap.set
      map("n", "<leader>fh", function() toggle_telescope(harpoon:list()) end, { desc = "Harpoon list" })
      map("n", "<leader>au", function() harpoon:list():replace_at(1) end)
      map("n", "<leader>ai", function() harpoon:list():replace_at(2) end)
      map("n", "<leader>ao", function() harpoon:list():replace_at(3) end)
      map("n", "<leader>ap", function() harpoon:list():replace_at(4) end)
      map("n", "<leader>u",  function() harpoon:list():select(1) end)
      map("n", "<leader>i",  function() harpoon:list():select(2) end)
      map("n", "<leader>o",  function() harpoon:list():select(3) end)
      map("n", "<leader>p",  function() harpoon:list():select(4) end)
    end,
  },

}
