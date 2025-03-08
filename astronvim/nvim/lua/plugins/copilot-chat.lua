---@type LazySpec
return {
  {
    "MeanderingProgrammer/render-markdown.nvim",
    optional = true,
    opts = {
      file_types = { "markdown", "copilot-chat" },
    },
    ft = { "markdown", "copilot-chat" },
  },
  {
    "CopilotC-Nvim/CopilotChat.nvim",
    cmd = { "CopilotChat" },
    dependencies = {
      { "zbirenbaum/copilot.lua" },
      { "nvim-lua/plenary.nvim", branch = "master" }, -- for curl, log and async functions
    },
    build = "make tiktoken", -- Only on MacOS or Linux
    opts = {
      window = {
        width = 0.4,
      },
      prompts = {
        Commit = {
          prompt = ""
            .. "Given the Git diff, generate a concise and descriptive Git commit message using Gitmoji conventions. "
            .. "Select the most appropriate emoji based on the changes and ensure the commit message is clear and within 72 characters. "
            .. "Optionally, include a short description if necessary.",
          sticky = "#git:staged",
        },
      },
      -- See Configuration section for options
    },
    keys = {
      { "<leader>a", "", mode = { "n", "v" }, desc = "+Copilot Chat" },
      -- CopilotChat-defined commands
      { "<leader>aa", "<cmd>CopilotChatToggle<cr>", mode = { "n", "v" }, desc = "Toggle" },
      { "<leader>ar", "<cmd>CopilotChatReset<cr>", desc = "Reset" },
      { "<leader>ac", "<cmd>CopilotChatCommit<cr>", desc = "Commit" },
      -- Custom commands
    },
    -- See Commands section for default commands if you want to lazy load on them
  },
}
