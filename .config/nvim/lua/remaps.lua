local map = vim.keymap.set
local opts = { noremap = true, silent = true }

-- System clipboard integration
map({ "n", "v" }, "y", '"+y', opts)
map("n", "yy", '"+yy', opts)
map({ "n", "v" }, "d", '"+d', opts)
map("n", "dd", '"+dd', opts)
map({ "n", "v" }, "p", '"+p', opts)
map({ "n", "v" }, "P", '"+P', opts)

-- Telescope
map("n", "<leader>ff", "<cmd>Telescope find_files<CR>", { desc = "Find Files" })
map("n", "<leader>fg", "<cmd>Telescope live_grep<CR>", { desc = "Live Grep" })

-- LSP keymaps
map("n", "gd", vim.lsp.buf.definition, {})
map("n", "gr", vim.lsp.buf.references, {})
map("n", "gI", vim.lsp.buf.implementation, {})
map("n", "gy", vim.lsp.buf.type_definition, {})
map("n", "gD", vim.lsp.buf.declaration, {})
map("n", "K", vim.lsp.buf.hover, {})
map("n", "gK", vim.lsp.buf.signature_help, {})
map("i", "<C-k>", vim.lsp.buf.signature_help, {})

map({ "n", "x" }, "<leader>ca", vim.lsp.buf.code_action, {})
map("n", "<leader>cr", vim.lsp.buf.rename, {})

map("n", "[d", vim.diagnostic.goto_prev, {})
map("n", "]d", vim.diagnostic.goto_next, {})
map("n", "<leader>e", vim.diagnostic.open_float, {})

-- Keep cursor centered after search and scroll
map("n", "n", "nzzzv", opts)
map("n", "N", "Nzzzv", opts)
map("n", "*", "*zzzv", opts)
map("n", "#", "#zzzv", opts)
map("n", "g*", "g*zzzv", opts)
map("n", "g#", "g#zzzv", opts)

-- Terminal
local terminal = require("terminal")
map("n", "<leader>t", terminal.summon_terminal, { desc = "Summon terminal (insert)" })

-- Language runners
local runners = require("runners")
map("n", "<leader>r", function()
	runners.run_current_file(terminal.term_send)
end, { desc = "Run (Rust/Java/C/C++/Python/HTML)" })

-- PlatformIO / Microcontroller
map("n", "<leader>sm", function() runners.pio_monitor(terminal.term_send) end,       { desc = "PIO: Serial Monitor" })