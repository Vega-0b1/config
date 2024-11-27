
local wezterm = require 'wezterm'


local config = wezterm.config_builder()


config.tab_bar_at_bottom = true
config.use_fancy_tab_bar = false
config.window_decorations = "RESIZE"

config.color_scheme = 'Catppuccin Latte'


return config
