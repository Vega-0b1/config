-- Language-specific compile and run utilities
local M = {}

local function project_root(markers)
	return vim.fs.root(0, markers) or vim.fn.expand("%:p:h")
end

function M.rust_run(term_send)
	if vim.fn.executable("cargo") == 0 then
		vim.notify("cargo not found in PATH", vim.log.levels.ERROR)
		return
	end
	vim.cmd("write")
	local root = project_root({ "Cargo.toml", ".git" })
	term_send(string.format("cd %q && cargo run", root))
end

function M.java_run(term_send)
	if vim.fn.executable("javac") == 0 then
		vim.notify("javac not found in PATH", vim.log.levels.ERROR)
		return
	end
	if vim.fn.executable("java") == 0 then
		vim.notify("java not found in PATH", vim.log.levels.ERROR)
		return
	end
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

function M.c_run(term_send)
	if vim.fn.executable("gcc") == 0 then
		vim.notify("gcc not found in PATH", vim.log.levels.ERROR)
		return
	end
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

function M.cpp_run(term_send)
	if vim.fn.executable("g++") == 0 then
		vim.notify("g++ not found in PATH", vim.log.levels.ERROR)
		return
	end
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

function M.python_run(term_send)
	if vim.fn.executable("python3") == 0 then
		vim.notify("python3 not found in PATH", vim.log.levels.ERROR)
		return
	end
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

function M.html_run(term_send)
	if vim.fn.executable("live-server") == 0 then
		vim.notify("live-server not found in PATH", vim.log.levels.ERROR)
		return
	end
	vim.cmd("write")
	-- Serve from the directory containing the HTML file
	local file_dir = vim.fn.expand("%:p:h")
	-- Force port 8080 and manually open browser
	term_send(string.format("cd %q && live-server -p 8080 . & sleep 1 && xdg-open http://127.0.0.1:8080", file_dir))
end

function M.run_current_file(term_send)
	local ft = vim.bo.filetype
	if ft == "rust" then
		M.rust_run(term_send)
	elseif ft == "java" then
		M.java_run(term_send)
	elseif ft == "c" then
		M.c_run(term_send)
	elseif ft == "cpp" or ft == "cc" or ft == "cxx" then
		M.cpp_run(term_send)
	elseif ft == "python" then
		M.python_run(term_send)
	elseif ft == "html" then
		M.html_run(term_send)
	else
		vim.notify("No runner for filetype: " .. (ft or "?"), vim.log.levels.WARN)
	end
end

return M
