return {
  "iamcco/markdown-preview.nvim",
  cmd = { "MarkdownPreviewToggle", "MarkdownPreview", "MarkdownPreviewStop" },
  ft = { "markdown" },
  build = function() vim.fn["mkdp#util#install"]() end,
  init = function()
    vim.g.mkdp_auto_start = 1
    vim.g.mkdp_open_to_the_world = 1
    vim.g.mkdp_port = 8080
    vim.g.mkdp_browser = "none"
    vim.g.mkdp_echo_preview_url = 1
  end,
}
