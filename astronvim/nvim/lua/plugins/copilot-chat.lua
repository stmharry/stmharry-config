---@type LazySpec
return {
  {
    "MeanderingProgrammer/render-markdown.nvim",
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
            .. 'A gitmoji commit message is in the format of "<intention> [scope?][:?] <message>" and is composed using the following pieces: \n'
            .. "- intention: The intention you want to express with the commit, using an emoji in unicode format. \n"
            .. "- scope: An optional string that adds contextual information for the scope of the change. \n"
            .. "- message: A brief explanation of the change. \n"
            .. ""
            .. "Examples: \n"
            .. "- ⚡️ Lazyload home screen images. \n"
            .. "- 🐛 Fix `onClick` event handler. \n"
            .. "- 🔖 Bump version `1.2.0` \n"
            .. "- ♻️ (components): Transform classes to hooks \n"
            .. "- 📈 Add analytics to the dashboard \n"
            .. "- 🌐 Support Japanese language \n"
            .. "- ♿️ (account): Improve modals a11y \n"
            .. ""
            .. "Select the most appropriate emoji based on the changes and ensure the commit message is clear and within 72 characters. "
            .. "Optionally, include a short description if necessary.",
          sticky = "#git:staged",
        },
      },
      -- See Configuration section for options
    },
    config = function(_, opts)
      local chat = require "CopilotChat"
      chat.setup(opts)

      local select = require "CopilotChat.select"
      vim.api.nvim_create_user_command(
        "CopilotChatBuffer",
        function(args) chat.ask(args.args, { selection = select.buffer }) end,
        { nargs = "*", range = true }
      )
    end,
    keys = {
      { "<leader>a", "", mode = { "n", "v" }, desc = "+Copilot Chat" },
      -- CopilotChat-defined commands
      { "<leader>at", "<cmd>CopilotChatToggle<cr>", mode = { "n", "v" }, desc = "Toggle Chat" },
      { "<leader>ar", "<cmd>CopilotChatReset<cr>", desc = "Reset Chat" },
      { "<leader>ac", "<cmd>CopilotChatCommit<cr>", desc = "Write Commit Message (with git diff)" },
      -- Custom commands
      {
        "<leader>aq",
        function()
          local input = vim.fn.input ":"
          if input ~= "" then vim.cmd("CopilotChatBuffer " .. input) end
        end,
        desc = "Quick Chat (with buffer)",
      },
    },
    -- See Commands section for default commands if you want to lazy load on them
  },
}
