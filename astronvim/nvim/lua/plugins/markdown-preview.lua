-- NOTE:
-- snatched from https://github.com/iamcco/markdown-preview.nvim/issues/690#issuecomment-2254280534

---@type LazySpec
return {
  "iamcco/markdown-preview.nvim",
  cmd = { "MarkdownPreviewToggle", "MarkdownPreview", "MarkdownPreviewStop" },
  ft = { "markdown" },
  build = function(plugin)
    if vim.fn.executable "npx" then
      vim.cmd("!cd " .. plugin.dir .. " && cd app && npx --yes yarn install")
    else
      vim.cmd [[Lazy load markdown-preview.nvim]]
      vim.fn["mkdp#util#install"]()
    end
  end,
  init = function()
    if vim.fn.executable "npx" then vim.g.mkdp_filetypes = { "markdown" } end

    vim.g.mkdp_auto_start = 1
    vim.g.mkdp_open_to_the_world = 1
    vim.g.mkdp_port = 8080
    vim.g.mkdp_browser = "none"
    vim.g.mkdp_echo_preview_url = 1
  end,
}
