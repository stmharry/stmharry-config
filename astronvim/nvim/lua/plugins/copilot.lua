---@type LazySpec
return {
  "zbirenbaum/copilot.lua",
  enabled = vim.env.STMHARRY_NVIM_COPILOT == "1",
  cmd = "Copilot",
  event = "InsertEnter",
  init = function() vim.g.copilot_filetypes = { markdown = true } end,
  opts = {
    panel = {
      enabled = true,
      auto_refresh = true,
      keymap = {
        jump_prev = "[[",
        jump_next = "]]",
        accept = "<CR>",
        refresh = "gr",
        open = "<M-CR>",
      },
      layout = {
        position = "bottom", -- | top | left | right
        ratio = 0.25,
      },
    },
    suggestion = {
      enabled = true,
      auto_trigger = true,
      debounce = 75,
      keymap = {
        accept = "<M-l>",
        accept_word = false,
        accept_line = false,
        next = "<M-]>",
        prev = "<M-[>",
        dismiss = "<C-]>",
      },
    },
    filetypes = {
      clojure = true,
      yaml = true,
      markdown = true,
      help = false,
      gitcommit = true,
      gitrebase = false,
      hgcommit = false,
      svn = false,
      cvs = false,
      ["."] = false,
    },
    copilot_node_command = "node", -- Use the declared Node LTS runtime.
    server_opts_overrides = {},
  },
}
