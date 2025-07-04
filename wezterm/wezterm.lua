local wezterm = require 'wezterm'
local act = wezterm.action
local config = wezterm.config_builder()

config.tab_bar_at_bottom = false
config.use_fancy_tab_bar = true 
config.window_decorations = 'RESIZE'
config.color_scheme = 'Dracula (base16)'

config.keys = {
  {
    key = 'q',
    mods = 'ALT',
    action = wezterm.action.CloseCurrentPane { confirm = true },
  },

  {
    key = 'j',
    mods = 'ALT|SHIFT',
    action = act.AdjustPaneSize { 'Down', 5 },
  },


  {
    key = 'k',
    mods = 'ALT|SHIFT',
    action = act.AdjustPaneSize { 'Up', 5 },
  },


  {
    key = 'h',
    mods = 'ALT|SHIFT',
    action = act.AdjustPaneSize { 'Left', 5 },
  },

  {
    key = 'l',
    mods = 'ALT|SHIFT',
    action = act.AdjustPaneSize { 'Right', 5 },
  },

  {
    key = 'v',
    mods = 'ALT|SHIFT',
    action = act.SplitVertical {},
  },

  {
    key = 'b',
    mods = 'ALT|SHIFT',
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
    mods = 'SHIFT|ALT',
    action = act.SpawnTab 'CurrentPaneDomain',
  },
  {
    key = 'h',
    mods = 'CTRL',
    action = act.ActivateTabRelative(-1),
  },
  {
    key = 'l',
    mods = 'CTRL',
    action = act.ActivateTabRelative(1),
  },
  {
    key = 'y',
    mods = 'CTRL',
    action = act.CopyTo 'Clipboard',
  }, {
  key = 'p',
  mods = 'CTRL',
  action = act.PasteFrom 'Clipboard',
},
}
return config
