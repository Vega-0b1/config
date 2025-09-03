-- rainbow-delimiters: default config
local rainbow_delimiters = require("rainbow-delimiters")

vim.g.rainbow_delimiters = {
  strategy = {
    [""] = rainbow_delimiters.strategy["global"],
    vim  = rainbow_delimiters.strategy["local"],
  },
  query = {
    [""] = "rainbow-delimiters",
    lua  = "rainbow-blocks",
  },
  highlight = {
    -- leave empty → plugin uses its built-in default colors
  },
}
