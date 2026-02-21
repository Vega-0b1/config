-- Terminal management utilities
local M = {}

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

function M.term_send(cmd)
	ensure_run_term()
	vim.fn.chansend(vim.b.terminal_job_id, cmd .. "\n")
	term_to_normal() -- stay in normal after launching
end

function M.summon_terminal()
	ensure_run_term()
	vim.schedule(function()
		vim.cmd("startinsert")
	end)
end

return M
