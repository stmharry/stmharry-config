-- NOTE:
-- snatched from https://github.com/iamcco/markdown-preview.nvim/issues/690#issuecomment-2254280534

---@type LazySpec
return {
  "iamcco/markdown-preview.nvim",
  cmd = { "MarkdownPreviewToggle", "MarkdownPreview", "MarkdownPreviewStop" },
  ft = { "markdown" },
  build = function(plugin)
    if vim.fn.executable "npx" == 1 then
      vim.cmd("!cd " .. vim.fn.shellescape(plugin.dir .. "/app") .. " && npx --yes yarn install")
    else
      vim.cmd [[Lazy load markdown-preview.nvim]]
      vim.fn["mkdp#util#install"]()
    end
  end,
  init = function()
    if vim.fn.executable "npx" == 1 then vim.g.mkdp_filetypes = { "markdown" } end

    vim.g.mkdp_auto_start = 0
    vim.g.mkdp_open_to_the_world = 0
    if vim.env.SSH_CONNECTION then vim.g.mkdp_browser = "none" end
    vim.g.mkdp_echo_preview_url = 1
  end,
}
