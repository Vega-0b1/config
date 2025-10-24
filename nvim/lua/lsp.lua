
-- Auto-format C/C++ with clangd on save (single, tidy place)
local aug = vim.api.nvim_create_augroup("ClangdFormat", { clear = true })

vim.api.nvim_create_autocmd("LspAttach", {
  group = aug,
  callback = function(args)
    local client = vim.lsp.get_client_by_id(args.data.client_id)
    local bufnr = args.buf
    if not client or client.name ~= "clangd" then return end

    -- Only for C/C++ buffers
    local ft = vim.bo[bufnr].filetype
    if ft ~= "c" and ft ~= "cpp" then return end

    -- Optional: ensure formatting is exposed
    client.server_capabilities.documentFormattingProvider = true

    -- Buffer-local save hook
    vim.api.nvim_create_autocmd("BufWritePre", {
      group = aug,
      buffer = bufnr,
      callback = function()
        if vim.g.disable_clangd_format or vim.b.disable_clangd_format then return end
        vim.lsp.buf.format({
          bufnr = bufnr,
          timeout_ms = 1500,
          filter = function(c) return c.name == "clangd" end,
        })
      end,
      desc = "Format C/C++ with clangd on save",
    })

    -- Optional: manual format keymap
    vim.keymap.set("n", "<leader>f", function()
      vim.lsp.buf.format({
        bufnr = bufnr, timeout_ms = 1500,
        filter = function(c) return c.name == "clangd" end,
      })
    end, { buffer = bufnr, desc = "Format with clangd" })
  end,
})
