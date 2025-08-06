local wezterm = require("wezterm")
local act = wezterm.action
local config = wezterm.config_builder()

config.color_scheme = "Dracula (base16)"

config.keys = {
	{
		key = "q",
		mods = "ALT",
		action = wezterm.action.CloseCurrentPane({ confirm = true }),
	},

	{
		key = "j",
		mods = "ALT|CTRL",
		action = act.AdjustPaneSize({ "Down", 5 }),
	},

	{
		key = "k",
		mods = "ALT|CTRL",
		action = act.AdjustPaneSize({ "Up", 5 }),
	},

	{
		key = "h",
		mods = "ALT|CTRL",
		action = act.AdjustPaneSize({ "Left", 5 }),
	},

	{
		key = "l",
		mods = "ALT|CTRL",
		action = act.AdjustPaneSize({ "Right", 5 }),
	},

	{
		key = "v",
		mods = "ALT|CTRL",
		action = act.SplitVertical({}),
	},

	{
		key = "b",
		mods = "ALT|CTRL",
		action = act.SplitHorizontal({}),
	},

	{
		key = "h",
		mods = "ALT",
		action = act.ActivatePaneDirection("Left"),
	},

	{
		key = "j",
		mods = "ALT",
		action = act.ActivatePaneDirection("Down"),
	},

	{
		key = "k",
		mods = "ALT",
		action = act.ActivatePaneDirection("Up"),
	},

	{
		key = "l",
		mods = "ALT",
		action = act.ActivatePaneDirection("Right"),
	},
	{
		key = "t",
		mods = "ALT|CTRL",
		action = act.SpawnTab("CurrentPaneDomain"),
	},
	{
		key = "h",
		mods = "ALT|SHIFT",
		action = act.ActivateTabRelative(-1),
	},
	{
		key = "l",
		mods = "ALT|SHIFT",
		action = act.ActivateTabRelative(1),
	},
	{
		key = "y",
		mods = "ALT",
		action = act.CopyTo("Clipboard"),
	},
	{
		key = "p",
		mods = "ALT",
		action = act.PasteFrom("Clipboard"),
	},
}
return config
