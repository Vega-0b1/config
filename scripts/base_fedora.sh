#!/bin/bash
dnf copr enable -y \
  wezfurlong/wezterm-nightly \
  lihaohong/yazi \
  agriffis/neovim-nightly

dnf install -y \
  git \
  wezterm \
  yazi \
  neovim \
  python3-neovim 

