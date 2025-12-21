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

-- Run current file/project in a bottom terminal (Rust/Java/C/C++/Python), reuse the same split
local runterm = { win = nil, buf = nil }

local function ensure_run_term()
	if runterm.win and vim.api.nvim_win_is_valid(runterm.win) then
		vim.api.nvim_set_current_win(runterm.win)
		return
	end

	vim.cmd("botright 20split | terminal") -- change 20 to 6/10/etc
	runterm.win = vim.api.nvim_get_current_win()
	runterm.buf = vim.api.nvim_get_current_buf()
	vim.wo.winfixheight = true

	-- close terminal split easily:
	vim.keymap.set("t", "<C-q>", [[<C-\><C-n><cmd>close<CR>]], { buffer = runterm.buf, silent = true })
	vim.keymap.set("n", "q", "<cmd>close<CR>", { buffer = runterm.buf, silent = true })
end

local function term_send(cmd)
	ensure_run_term()
	vim.fn.chansend(vim.b.terminal_job_id, cmd .. "\n")
	vim.cmd("startinsert")
end

local function project_root(markers)
	return vim.fs.root(0, markers) or vim.fn.expand("%:p:h")
end

local function rust_run()
	vim.cmd("write")
	local root = project_root({ "Cargo.toml", ".git" })
	term_send(string.format("cd %q && cargo run", root))
end

local function java_run()
	vim.cmd("write")

	local file = vim.fn.expand("%:p")
	local class = vim.fn.expand("%:t:r")

	local pkg
	for i = 1, math.min(50, vim.fn.line("$")) do
		local line = vim.fn.getline(i)
		pkg = line:match("^%s*package%s+([%w%.]+)%s*;")
		if pkg then
			break
		end
	end
	local fqcn = pkg and (pkg .. "." .. class) or class

	local root = project_root({ "pom.xml", "build.gradle", "settings.gradle", ".git" })
	local outdir = root .. "/.nvim-java"
	vim.fn.mkdir(outdir, "p")

	local cmd = string.format("cd %q && javac -d %q %q && java -cp %q %s", root, outdir, file, outdir, fqcn)
	term_send(cmd)
end

local function c_run()
	vim.cmd("write")

	local file = vim.fn.expand("%:p")
	local name = vim.fn.expand("%:t:r")
	local root = project_root({ "compile_commands.json", "CMakeLists.txt", "Makefile", ".git" })

	local bindir = root .. "/.nvim-bin"
	vim.fn.mkdir(bindir, "p")
	local exe = bindir .. "/" .. name

	local cmd = string.format("cd %q && gcc -std=c11 -Wall -Wextra -O0 -g %q -o %q && %q", root, file, exe, exe)
	term_send(cmd)
end

local function cpp_run()
	vim.cmd("write")

	local file = vim.fn.expand("%:p")
	local name = vim.fn.expand("%:t:r")
	local root = project_root({ "compile_commands.json", "CMakeLists.txt", "Makefile", ".git" })

	local bindir = root .. "/.nvim-bin"
	vim.fn.mkdir(bindir, "p")
	local exe = bindir .. "/" .. name

	local cmd = string.format("cd %q && g++ -std=c++20 -Wall -Wextra -O0 -g %q -o %q && %q", root, file, exe, exe)
	term_send(cmd)
end

local function python_run()
	vim.cmd("write")
	local file = vim.fn.expand("%:p")
	local root = project_root({ "pyproject.toml", "requirements.txt", ".git" })
	-- uses python3 from your PATH (Arch: usually available)
	term_send(string.format("cd %q && python3 %q", root, file))
end

map("n", "<leader>r", function()
	local ft = vim.bo.filetype
	if ft == "rust" then
		rust_run()
	elseif ft == "java" then
		java_run()
	elseif ft == "c" then
		c_run()
	elseif ft == "cpp" or ft == "cc" or ft == "cxx" then
		cpp_run()
	elseif ft == "python" then
		python_run()
	else
		vim.notify("No runner for filetype: " .. (ft or "?"), vim.log.levels.WARN)
	end
end, { desc = "Run (Rust/Java/C/C++/Python)" })
