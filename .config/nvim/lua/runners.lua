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
  term_send("clear")
  term_send(string.format("echo && cd %q && cargo run; S=$?; echo; echo; echo '[exit status]:' $S", root))
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
    if pkg then break end
  end
  local fqcn = pkg and (pkg .. "." .. class) or class

  local root = project_root({ "pom.xml", "build.gradle", "settings.gradle", ".git" })
  local outdir = root .. "/.nvim-java"
  vim.fn.mkdir(outdir, "p")

  term_send("clear")
  term_send(string.format("echo && cd %q && javac -d %q %q && echo && echo '[stdout]:' && java -cp %q %s; S=$?; echo; echo; echo '[exit status]:' $S", root, outdir, file, outdir, fqcn))
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
  local file_dir = vim.fn.expand("%:p:h")

  term_send("clear")
  term_send(string.format("echo && cd %q && gcc -std=gnu11 -Wall -Wextra -O0 -g %q -o %q -lrt && echo && echo '[stdout]:' && cd %q && %q; S=$?; echo; echo; echo '[exit status]:' $S", root, file, exe, file_dir, exe))
end

function M.cmake_run(term_send)
  if vim.fn.executable("cmake") == 0 then
    vim.notify("cmake not found in PATH", vim.log.levels.ERROR)
    return
  end
  vim.cmd("write")

  local root = project_root({ "CMakeLists.txt", ".git" })
  local cmake_file = root .. "/CMakeLists.txt"

  local exe_name
  for line in io.lines(cmake_file) do
    exe_name = line:match("qt_add_executable%s*%(%s*(%S+)")
      or line:match("add_executable%s*%(%s*(%S+)")
    if exe_name then break end
  end

  if not exe_name then
    vim.notify("Could not find executable target in CMakeLists.txt", vim.log.levels.ERROR)
    return
  end

  local exe = string.format("%s/build/%s", root, exe_name)
  term_send("clear")
  term_send(string.format("echo && cd %q && cmake -B build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON && cmake --build build && echo && echo '[stdout]:' && %q; S=$?; echo; echo; echo '[exit status]:' $S", root, exe))
end

function M.cpp_run(term_send)
  vim.cmd("write")

  local root = project_root({ "compile_commands.json", "CMakeLists.txt", "Makefile", ".git" })

  if vim.fn.filereadable(root .. "/CMakeLists.txt") == 1 then
    M.cmake_run(term_send)
    return
  end

  if vim.fn.executable("g++") == 0 then
    vim.notify("g++ not found in PATH", vim.log.levels.ERROR)
    return
  end

  local file = vim.fn.expand("%:p")
  local name = vim.fn.expand("%:t:r")
  local bindir = root .. "/.nvim-bin"
  vim.fn.mkdir(bindir, "p")
  local exe = bindir .. "/" .. name
  local file_dir = vim.fn.expand("%:p:h")

  term_send("clear")
  term_send(string.format("echo && cd %q && g++ -std=c++20 -Wall -Wextra -O0 -g %q -o %q && echo && echo '[stdout]:' && cd %q && %q; S=$?; echo; echo; echo '[exit status]:' $S", root, file, exe, file_dir, exe))
end

function M.python_run(term_send)
  if vim.fn.executable("python3") == 0 then
    vim.notify("python3 not found in PATH", vim.log.levels.ERROR)
    return
  end
  vim.cmd("write")
  local file = vim.fn.expand("%:p")

  local root = project_root({ "pyproject.toml", "requirements.txt", ".git" })

  local main_path = vim.fs.find("__main__.py", {
    path = vim.fn.expand("%:p:h"),
    upward = true,
    stop = root,
  })[1]

  if main_path then
    local pkg_dir = vim.fn.fnamemodify(main_path, ":h")
    local pkg_name = vim.fn.fnamemodify(pkg_dir, ":t")
    local parent = vim.fn.fnamemodify(pkg_dir, ":h")
    term_send("clear")
    term_send(string.format("echo && echo '[stdout]:' && cd %q && python3 -m %s; S=$?; echo; echo; echo '[exit status]:' $S", parent, pkg_name))
    return
  end

  local file_dir = vim.fn.expand("%:p:h")
  term_send("clear")
  term_send(string.format("echo && echo '[stdout]:' && cd %q && python3 %q; S=$?; echo; echo; echo '[exit status]:' $S", file_dir, file))
end

function M.html_run(term_send)
  if vim.fn.executable("live-server") == 0 then
    vim.notify("live-server not found in PATH", vim.log.levels.ERROR)
    return
  end
  vim.cmd("write")
  local file_dir = vim.fn.expand("%:p:h")
  term_send("clear")
  term_send(string.format("cd %q && pkill -f 'live-server' 2>/dev/null; live-server -p 8080 . & sleep 1 && xdg-open http://127.0.0.1:8080", file_dir))
end

function M.kotlin_run(term_send)
  if vim.fn.executable("kotlinc") == 0 then
    vim.notify("kotlinc not found in PATH", vim.log.levels.ERROR)
    return
  end
  vim.cmd("write")

  local file = vim.fn.expand("%:p")
  local name = vim.fn.expand("%:t:r")
  local root = project_root({ "build.gradle", "settings.gradle", ".git" })

  local outdir = root .. "/.nvim-kotlin"
  vim.fn.mkdir(outdir, "p")
  local jar = outdir .. "/" .. name .. ".jar"

  term_send("clear")
  term_send(string.format("echo && cd %q && kotlinc %q -include-runtime -d %q && echo && echo '[stdout]:' && java -jar %q; S=$?; echo; echo; echo '[exit status]:' $S", root, file, jar, jar))
end

function M.pio_run(term_send, target)
  if vim.fn.executable("pio") == 0 then
    vim.notify("pio not found in PATH", vim.log.levels.ERROR)
    return
  end
  vim.cmd("write")
  local root = vim.fs.root(0, { "platformio.ini" })
  if not root then
    vim.notify("No platformio.ini found", vim.log.levels.ERROR)
    return
  end
  local has_compiledb = vim.fn.filereadable(root .. "/compile_commands.json") == 1
  local base = target
    and string.format("cd %q && pio run -t %s", root, target)
    or string.format("cd %q && pio run", root)
  local cmd = has_compiledb
    and base
    or base .. string.format(" && pio run -t compiledb && cp .pio/build/$(ls .pio/build | head -1)/compile_commands.json %q", root)
  term_send("clear")
  term_send(cmd)
end

function M.pio_monitor(term_send)
  if vim.fn.executable("pio") == 0 then
    vim.notify("pio not found in PATH", vim.log.levels.ERROR)
    return
  end
  local root = vim.fs.root(0, { "platformio.ini" })
  if not root then
    vim.notify("No platformio.ini found", vim.log.levels.ERROR)
    return
  end
  term_send(string.format("cd %q && pio device monitor", root))
end

function M.run_current_file(term_send)
  local ft = vim.bo.filetype
  if ft == "rust" then
    M.rust_run(term_send)
  elseif ft == "java" then
    M.java_run(term_send)
  elseif ft == "c" then
    if vim.fs.root(0, { "platformio.ini" }) then
      M.pio_run(term_send, "upload")
    else
      M.c_run(term_send)
    end
  elseif ft == "cpp" or ft == "cc" or ft == "cxx" then
    if vim.fs.root(0, { "platformio.ini" }) then
      M.pio_run(term_send, "upload")
    else
      M.cpp_run(term_send)
    end
  elseif ft == "python" then
    M.python_run(term_send)
  elseif ft == "html" then
    M.html_run(term_send)
  elseif ft == "kotlin" then
    M.kotlin_run(term_send)
  else
    vim.notify("No runner for filetype: " .. (ft or "?"), vim.log.levels.WARN)
  end
end

return M
