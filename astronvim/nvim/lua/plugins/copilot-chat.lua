---@type LazySpec
return {
  {
    "CopilotC-Nvim/CopilotChat.nvim",
    cmd = { "CopilotChat" },
    dependencies = {
      { "zbirenbaum/copilot.lua" },
      { "nvim-lua/plenary.nvim", branch = "master" }, -- for curl, log and async functions
    },
    build = "make tiktoken", -- Only on MacOS or Linux
    opts = {
      -- See Configuration section for options
    },
    keys = {
      { "<leader>a", "", desc = "+Copilot Chat", mode = { "n", "v" } },
      {
        "<leader>aa",
        function() return require("CopilotChat").toggle() end,
        desc = "Toggle",
        mode = { "n", "v" },
      },
      {
        "<leader>ac",
        "<cmd>CopilotChatCommit<cr>",
        desc = "Commit",
      },
    },
    -- See Commands section for default commands if you want to lazy load on them
  },
}
