return {
	"windwp/nvim-autopairs",
	event = "InsertEnter",
	config = function()
		local npairs = require("nvim-autopairs")
		local Rule = require("nvim-autopairs.rule")
		local cond = require("nvim-autopairs.conds")

		npairs.setup({
			check_ts = true, -- uses treesitter if available
			disable_filetype = { "TelescopePrompt", "vim" },
			fast_wrap = {
				map = "<M-e>",
				chars = { "{", "[", "(", '"', "'", "`" },
				pattern = [=[[%'%"%>%]%)%}%,]]=],
				end_key = "$",
				keys = "qwertyuiopzxcvbnmasdfghjkl",
				check_comma = true,
				highlight = "Search",
				highlight_grey = "Comment",
			},
		})

		-- Common HTML/JSX nicety: add space inside () when you type "( "
		npairs.add_rules({
			Rule(" ", " ")
				:with_pair(function(opts)
					local pair = opts.line:sub(opts.col - 1, opts.col)
					return pair == "()" or pair == "[]" or pair == "{}"
				end)
				:with_move(cond.none())
				:with_cr(cond.none())
				:with_del(function(opts)
					local pair = opts.line:sub(opts.col - 1, opts.col)
					return pair == "  "
				end),
		})
	end,
}
