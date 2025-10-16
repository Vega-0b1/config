local map = vim.keymap.set
local opts = { noremap = true, silent = true }

-- Clipboard
map({ "n", "v" }, "y", '"+y', opts)
map("n", "yy", '"+yy', opts)
map({ "n", "v" }, "p", '"+p', opts)
map({ "n", "v" }, "P", '"+P', opts)

-- Telescope
map("n", "<leader>ff", "<cmd>Telescope find_files<CR>", { desc = "Find Files" })
map("n", "<leader>fg", "<cmd>Telescope live_grep<CR>", { desc = "Live Grep" })

-- File Explorer (Oil)
map("n", "-", function()
	require("oil").open()
end, { desc = "Open parent directory" })

-- LSP keymaps
map("n", "gd", vim.lsp.buf.definition, {})
map("n", "K", vim.lsp.buf.hover, {})
map("n", "<leader>rn", vim.lsp.buf.rename, {})
map("n", "<leader>ca", vim.lsp.buf.code_action, {})
map("n", "[d", vim.diagnostic.goto_prev, {})
map("n", "]d", vim.diagnostic.goto_next, {})

-- Escape in terminal: switch to normal mode
map("t", "<Esc>", [[<C-\><C-n>]], { noremap = true, silent = true, desc = "Exit terminal mode" })

-- Keep cursor centered after search and scroll
map("n", "n", "nzzzv", opts)
map("n", "N", "Nzzzv", opts)
map("n", "*", "*zzzv", opts)
map("n", "#", "#zzzv", opts)
map("n", "g*", "g*zzzv", opts)
map("n", "g#", "g#zzzv", opts)

map("n", "<C-d>", "<C-d>zz", opts)
map("n", "<C-u>", "<C-u>zz", opts)
map("n", "<C-f>", "<C-f>zz", opts)
map("n", "<C-b>", "<C-b>zz", opts)
