local wezterm = require 'wezterm'
local act = wezterm.action
local config = wezterm.config_builder()

config.tab_bar_at_bottom = true
config.use_fancy_tab_bar = true
config.window_decorations = 'NONE'
config.color_scheme = 'Dracula (base16)'

config.keys = {
  {
    key = 'q',
    mods = 'CTRL',
    action = wezterm.action.CloseCurrentPane { confirm = true},
  },

  {
    key = 'j',
    mods = 'SHIFT|CTRL',
    action = act.AdjustPaneSize { 'Down', 5 },
  },

  
  {
    key = 'k',
    mods = 'SHIFT|CTRL',
    action = act.AdjustPaneSize { 'Up', 5 },
  },

  
  {
    key = 'h',
    mods = 'SHIFT|CTRL',
    action = act.AdjustPaneSize { 'Left', 5 },
  },
  
  {
    key = 'l',
    mods = 'SHIFT|CTRL',
    action = act.AdjustPaneSize { 'Right', 5 },
  },

  {
    key = 'v',
    mods = 'SHIFT|CTRL',
    action = act.SplitVertical {},
  },

  {
    key = 'b',
    mods = 'SHIFT|CTRL',
    action = act.SplitHorizontal {},
  },

  {
    key = 'h',
    mods = 'ALT',
    action = act.ActivatePaneDirection 'Left',
  },

  
  {
    key = 'j',
    mods = 'ALT',
    action = act.ActivatePaneDirection 'Down',
  },

  
  {
    key = 'k',
    mods = 'ALT',
    action = act.ActivatePaneDirection 'Up',
  },

  
  {
    key = 'l',
    mods = 'ALT',
    action = act.ActivatePaneDirection 'Right',
  },
  {
    key = 't',
    mods = 'SHIFT|CTRL',
    action = act.SpawnTab 'CurrentPaneDomain',
  },
  {
    key = 'h',
    mods = 'ALT',
    action = act.ActivateTabRelative(-1), 
  },
   {
    key = 'l',
    mods = 'ALT',
    action = act.ActivateTabRelative(1), 
  }, 
}
return config
