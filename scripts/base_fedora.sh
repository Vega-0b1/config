#!/bin/bash
<<<<<<< HEAD
dnf copr enable -y wezfurlong/wezterm-nightly
dnf copr enable -y lihaohong/yazi 
dnf copr enable -y agriffis/neovim-nightly
=======
dnf copr enable -y \
  wezfurlong/wezterm-nightly \
  lihaohong/yazi \
  agriffis/neovim-nightly
>>>>>>> 4ab47530a9902717e3ff96f2423f22513e8cd250

dnf install -y \
  git \
  wezterm \
  yazi \
  neovim \
<<<<<<< HEAD
  python3-neovim \
  clang \
  clang-tools-extra \
  black \
  rust \
  cargo

cargo install stylua
export PATH="$HOME/.cargo/bin:$PATH"
=======
  python3-neovim 

>>>>>>> 4ab47530a9902717e3ff96f2423f22513e8cd250
