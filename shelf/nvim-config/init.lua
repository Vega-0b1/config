vim.g.mapleader = " "  -- must be set before any <leader> keymaps

vim.opt.shortmess:append("I")
vim.opt.modeline = false
vim.opt.splitbelow = true
vim.opt.scrolloff = 999
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.termguicolors = true
vim.opt.signcolumn = "yes"
vim.opt.updatetime = 300
vim.opt.cursorline = true
vim.opt.expandtab = true
vim.opt.shiftwidth = 2
vim.opt.tabstop = 2
vim.opt.undofile = true
vim.opt.undodir = vim.fn.stdpath("data") .. "/undo"

vim.diagnostic.config({
  virtual_text = {
    spacing = 4,
    prefix = "·",
  },
})

require("remaps")
require("dracula").setup({ transparent_bg = true })

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
vim.cmd.colorscheme("kanagawa-wave")

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

local capabilities = require("blink.cmp").get_lsp_capabilities(
  vim.lsp.protocol.make_client_capabilities()
)

vim.lsp.config("rust_analyzer", { capabilities = capabilities })
vim.lsp.enable("rust_analyzer")

vim.lsp.config("pyright", { capabilities = capabilities })
vim.lsp.enable("pyright")

vim.lsp.config("jdtls", { capabilities = capabilities })
vim.lsp.enable("jdtls")

vim.lsp.config("clangd", {
  capabilities = capabilities,
  cmd = { "clangd", "--function-arg-placeholders=false" },
})
vim.lsp.enable("clangd")

vim.lsp.config("ts_ls", { capabilities = capabilities })
vim.lsp.enable("ts_ls")

vim.lsp.config("html", { capabilities = capabilities })
vim.lsp.enable("html")

vim.lsp.config("cssls", { capabilities = capabilities })
vim.lsp.enable("cssls")

vim.lsp.config("lua_ls", {
  capabilities = capabilities,
  settings = {
    Lua = {
      diagnostics = { globals = { "vim" } },
      workspace   = { checkThirdParty = false },
      telemetry   = { enable = false },
    },
  },
})
vim.lsp.enable("lua_ls")

vim.lsp.config("bashls", { capabilities = capabilities })
vim.lsp.enable("bashls")

vim.lsp.config("kotlin_language_server", { capabilities = capabilities })
vim.lsp.enable("kotlin_language_server")

require("nvim-treesitter.configs").setup({
  highlight = { enable = true },
  indent    = { enable = true },
})

require("nvim-ts-autotag").setup({
  opts = {
    enable_close          = true,
    enable_rename         = true,
    enable_close_on_slash = false,
  },
})

-- keybinds in remaps.lua
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
    nix             = { "nixfmt" },
  },
  format_on_save = { timeout_ms = 1000, lsp_format = "fallback" },
})

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

require("notify").setup({
  stages  = "static",
  timeout = 800,
})

require("noice").setup({
  lsp = {
    progress = { enabled = false },
    override = {
      ["vim.lsp.util.convert_input_to_markdown_lines"] = true,
      ["vim.lsp.util.stylize_markdown"]                = true,
    },
  },
  presets = {
    bottom_search        = true,
    command_palette      = true,
    long_message_to_split = true,
    inc_rename           = false,
    lsp_doc_border       = false,
  },
  views = {
    notify = { timeout = 1500 },
    mini   = { timeout = 1500 },
  },
})

require("ibl").setup()
local function set_highlights()
  vim.api.nvim_set_hl(0, "RainbowDelimiterRed",    { fg = "#E05555" })
  vim.api.nvim_set_hl(0, "RainbowDelimiterYellow", { fg = "#F1FA8C" })
  vim.api.nvim_set_hl(0, "RainbowDelimiterBlue",   { fg = "#82AAFF" })
  vim.api.nvim_set_hl(0, "RainbowDelimiterOrange", { fg = "#FFB86C" })
  vim.api.nvim_set_hl(0, "RainbowDelimiterGreen",  { fg = "#50FA7B" })
  vim.api.nvim_set_hl(0, "RainbowDelimiterViolet", { fg = "#FF79C6" })
  vim.api.nvim_set_hl(0, "RainbowDelimiterCyan",   { fg = "#8BE9FD" })
end
set_highlights()
vim.api.nvim_create_autocmd("ColorScheme", { callback = set_highlights })

require("scrollEOF").setup()
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
