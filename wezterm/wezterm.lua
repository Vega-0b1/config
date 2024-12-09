local wezterm = require 'wezterm'
local act = wezterm.action
local config = wezterm.config_builder()

config.tab_bar_at_bottom = true
config.use_fancy_tab_bar = false
config.window_decorations = "RESIZE"
config.color_scheme = 'dracula'

config.keys = {
  {
    key = 'q',
    mods = 'SUPER',
    action = wezterm.action.CloseCurrentPane { confirm = true},
  },

  {
    key = 'j',
    mods = 'SUPER|SHIFT',
    action = act.AdjustPaneSize { 'Down', 5 },
  },

  
  {
    key = 'k',
    mods = 'SUPER|SHIFT',
    action = act.AdjustPaneSize { 'Up', 5 },
  },

  
  {
    key = 'h',
    mods = 'SUPER|SHIFT',
    action = act.AdjustPaneSize { 'Left', 5 },
  },
  
  {
    key = 'l',
    mods = 'SUPER|SHIFT',
    action = act.AdjustPaneSize { 'Right', 5 },
  },

  {
    key = 'v',
    mods = 'SUPER',
    action = act.SplitVertical {},
  },

  {
    key = 'b',
    mods = 'SUPER',
    action = act.SplitHorizontal {},
  },

  {
    key = 'h',
    mods = 'SUPER',
    action = act.ActivatePaneDirection 'Left',
  },

  
  {
    key = 'j',
    mods = 'SUPER',
    action = act.ActivatePaneDirection 'Down',
  },

  
  {
    key = 'k',
    mods = 'SUPER',
    action = act.ActivatePaneDirection 'Up',
  },

  
  {
    key = 'l',
    mods = 'SUPER',
    action = act.ActivatePaneDirection 'Right',
  },
  
}
return config
