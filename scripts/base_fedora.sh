#!/bin/bash
dnf copr enable -y wezfurlong/wezterm-nightly
dnf copr enable -y lihaohong/yazi 
dnf copr enable -y agriffis/neovim-nightly

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
  cargo \
  zsh \
  zsh-autosuggestions \
  zsh-syntax-highlighting
 chsh -s $(which zsh) jcvega
 curl -sS https://starship.rs/install.sh | sh

 
cargo install stylua
cargo install kanata
export PATH="$HOME/.cargo/bin:$PATH"

