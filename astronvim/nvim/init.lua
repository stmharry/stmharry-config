-- Bootstrap lazy.nvim; fail promptly in unattended setup if cloning fails.
local lazypath = vim.env.LAZY or vim.fn.stdpath "data" .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local result = vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable", "https://github.com/folke/lazy.nvim.git", lazypath })
  if vim.v.shell_error ~= 0 then error("Unable to clone lazy.nvim: " .. result) end
end
vim.opt.rtp:prepend(lazypath)
require "lazy_setup"
