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
            .. "# Gitmoji-Style Commit Message Generator Prompt\n"
            .. "\n"
            .. "You are an AI assistant that writes Gitmoji-style commit messages.\n"
            .. "\n"
            .. "---\n"
            .. "\n"
            .. "## Input\n"
            .. "```\n"
            .. "\n"
            .. "<REPO_ROOT>\n"
            .. "<git diff --staged or unified diff output>\n"
            .. "\n"
            .. "```\n"
            .. "\n"
            .. "## Task\n"
            .. "1. Analyze the diff and identify the **primary change type** (e.g., feature, fix, docs, style, refactor, perf, test, build, ci, chore, revert).  \n"
            .. "2. Select the appropriate **Gitmoji** for that change:\n"
            .. "   - ✨ `feat` — new feature  \n"
            .. "   - 🐛 `fix` — bug fix  \n"
            .. "   - 📝 `docs` — documentation only  \n"
            .. "   - 💄 `style` — formatting, whitespace, etc.  \n"
            .. "   - ♻️ `refactor` — code refactoring  \n"
            .. "   - ⚡️ `perf` — performance improvement  \n"
            .. "   - ✅ `test` — tests added or updated  \n"
            .. "   - 🔧 `build` — build system or dependencies  \n"
            .. "   - 👷 `ci` — CI configuration  \n"
            .. "   - 🔒 `chore` — other non-src/non-test changes  \n"
            .. "   - ⏪️ `revert` — revert a previous commit  \n"
            .. "3. Optionally infer a **scope** from file paths or module names.  \n"
            .. "4. Craft a **concise, imperative** subject line (≤ 50 characters).  \n"
            .. "5. If needed, write an optional **body** (wrapped at 72 characters) explaining *what* and *why*.  \n"
            .. "6. If applicable, include an optional **footer** for issue IDs or co-authors.  \n"
            .. "\n"
            .. "## Output Format\n"
            .. "```\n"
            .. "\n"
            .. "<emoji> [(scope)]: <imperative subject>\n"
            .. "\n"
            .. "[optional body]\n"
            .. "\n"
            .. "[optional footer]\n"
            .. "\n"
            .. "````\n"
            .. "\n"
            .. "## Example\n"
            .. "\n"
            .. "**Input:**\n"
            .. "```diff\n"
            .. "diff --git a/src/parser.js b/src/parser.js\n"
            .. "index 3e5e1f0..4b8c7a2 100644\n"
            .. "--- a/src/parser.js\n"
            .. "+++ b/src/parser.js\n"
            .. "@@ -10,6 +10,10 @@ function parse(input) {\n"
            .. "     // existing code\n"
            .. " }\n"
            .. "+  \n"
            .. "+// Added JSON support  \n"
            .. "+export function parseJSON(input) {  \n"
            .. "+  return JSON.parse(input);  \n"
            .. "}  \n"
            .. "````\n"
            .. "\n"
            .. "**Expected Output:**\n"
            .. "\n"
            .. "```\n"
            .. "✨ (parser): add support for JSON parsing\n"
            .. "```\n",
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
