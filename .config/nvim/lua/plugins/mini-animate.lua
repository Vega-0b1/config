return {
  "echasnovski/mini.animate",
  version = false,
  config = function()
    local animate = require("mini.animate")
    animate.setup({
      scroll = {
        timing = animate.gen_timing.linear({ duration = 100, unit = "total" }),
      },
      cursor = {
        timing = animate.gen_timing.linear({ duration = 80, unit = "total" }),
      },
      resize = { enable = false },
      open = { enable = false },
      close = { enable = false },
    })
  end,
}
