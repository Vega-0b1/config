local map = vim.keymap.set
local opts = { noremap = true, silent = true }

map({ "n", "v" }, "y", '"+y', opts)
map("n", "yy", '"+yy', opts)
map({ "n", "v" }, "p", '"+p', opts)
map({ "n", "v" }, "P", '"+P', opts)

-- Telescope
map("n", "<leader>ff", "<cmd>Telescope find_files<CR>", { desc = "Find Files" })
map("n", "<leader>fg", "<cmd>Telescope live_grep<CR>", { desc = "Live Grep" })

--harpoon stuff
local harpoon = require("harpoon")
harpoon:setup({})

-- basic telescope configuration
local conf = require("telescope.config").values
local function toggle_telescope(harpoon_files)
	local file_paths = {}
	for _, item in ipairs(harpoon_files.items) do
		table.insert(file_paths, item.value)
	end

	require("telescope.pickers")
		.new({}, {
			prompt_title = "Harpoon",
			finder = require("telescope.finders").new_table({
				results = file_paths,
			}),
			previewer = conf.file_previewer({}),
			sorter = conf.generic_sorter({}),
		})
		:find()
end

map("n", "<C-e>", function()
	toggle_telescope(harpoon:list())
end, { desc = "Open harpoon window" })
map("n", "<leader>a", function()
	harpoon:list():add()
end)

map("n", "<leader>u", function()
	harpoon:list():select(1)
end)
map("n", "<leader>i", function()
	harpoon:list():select(2)
end)
map("n", "<leader>o", function()
	harpoon:list():select(3)
end)
map("n", "<leader>p", function()
	harpoon:list():select(4)
end)

-- Toggle previous & next buffers stored within Harpoon list
map("n", "<C-S-P>", function()
	harpoon:list():prev()
end)
map("n", "<C-S-N>", function()
	harpoon:list():next()
end)

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

map("n", "<C-d>", "<C-d>zz", opts)
map("n", "<C-u>", "<C-u>zz", opts)
map("n", "<C-f>", "<C-f>zz", opts)
map("n", "<C-b>", "<C-b>zz", opts)

------------------------------------------------------------------------------------------------------------------------
---Terminal Stuff
------------------------------------------------------------------------------------------------------------------------
local runterm = { win = nil, buf = nil }

local function term_to_normal()
	local keys = vim.api.nvim_replace_termcodes("<C-\\><C-n>", true, false, true)
	vim.api.nvim_feedkeys(keys, "n", false)
end

local function ensure_run_term()
	if runterm.win and vim.api.nvim_win_is_valid(runterm.win) then
		vim.api.nvim_set_current_win(runterm.win)
		return
	end

	vim.cmd("botright 20split | terminal")
	runterm.win = vim.api.nvim_get_current_win()
	runterm.buf = vim.api.nvim_get_current_buf()
	vim.wo.winfixheight = true

	-- Start in terminal-normal so 'q' closes immediately
	term_to_normal()

	-- In this run terminal: q closes, i enters terminal input
	-- terminal-mode -> terminal-normal
	vim.keymap.set("t", "<Esc>", "<C-\\><C-n>", { buffer = runterm.buf, silent = true, desc = "Terminal normal mode" })
	vim.keymap.set("n", "q", "<cmd>close<CR>", { buffer = runterm.buf, silent = true })
	vim.keymap.set("n", "i", "<cmd>startinsert<CR>", { buffer = runterm.buf, silent = true })

	-- Optional: allow Ctrl-q to close even if you manually go into terminal input
	vim.keymap.set("t", "<C-q>", [[<C-\><C-n><cmd>close<CR>]], { buffer = runterm.buf, silent = true })
end

local function term_send(cmd)
	ensure_run_term()
	vim.fn.chansend(vim.b.terminal_job_id, cmd .. "\n")
	term_to_normal() -- stay in normal after launching
end

------------------------------------------------------------------------------------------------------------------------
---Compile and run
------------------------------------------------------------------------------------------------------------------------
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

	-- project root for "plain file" runs
	local root = project_root({ "pyproject.toml", "requirements.txt", ".git" })

	-- If we're inside a runnable package (has __main__.py), run `python -m <pkg>`
	local main_path = vim.fs.find("__main__.py", {
		path = vim.fn.expand("%:p:h"),
		upward = true,
		stop = root,
	})[1]

	if main_path then
		-- package dir is the folder containing __main__.py
		local pkg_dir = vim.fn.fnamemodify(main_path, ":h")
		local pkg_name = vim.fn.fnamemodify(pkg_dir, ":t")
		local parent = vim.fn.fnamemodify(pkg_dir, ":h")

		term_send(string.format("cd %q && python3 -m %s", parent, pkg_name))
		return
	end

	-- fallback: run current file
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
