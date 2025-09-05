#!/bin/bash
dnf copr enable -y wezfurlong/wezterm-nightly
dnf copr enable -y lihaohong/yazi 
dnf copr enable -y agriffis/neovim-nightly
=======
dnf copr enable -y \
  wezfurlong/wezterm-nightly \
  lihaohong/yazi \
  agriffis/neovim-nightly

dnf install -y \
  git \
  wezterm \
  yazi \
  neovim \
  python3-neovim \
  clang \
  clang-tools-extra \
  black \
  rust \
  cargo

cargo install stylua
export PATH="$HOME/.cargo/bin:$PATH"
  python3-neovim 

