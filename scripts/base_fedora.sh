#!/bin/bash
dnf copr enable -y lihaohong/yazi 
dnf copr enable -y agriffis/neovim-nightly
dnf copr enable -y solopasha/hyprland

dnf install \
  git \
  yazi \
  alacritty \
  firefox \
  neovim \
  python3-neovim \
  clang \
  clang-tools-extra \
  black \
  rust \
  cargo \
  zsh \
  zsh-autosuggestions \
  zsh-syntax-highlighting \
  sddm \
  hyprland \
  thunar \
  thunar-archive-plugin \
  thunar-volman \



dnf install \
  tar \
  wireplumber \
  upower \
  libgtop2 \
  bluez \
  bluez-tools \
  grimblast \
  hyprpicker \
  btop \
  NetworkManager \
  wl-clipboard \
  swww \
  brightnessctl \
  gnome-bluetooth \
  power-profiles-daemon \
  gvfs \
  nodejs \
  gtksourceview3 \
  libsoup3 \
  hyprpanel

cp /home/jcvega/.config/zsh/.zshrc /home/jcvega/.zshrc
chsh -s $(which zsh) jcvega
curl -sS https://starship.rs/install.sh | sh
 
cargo install stylua
cargo install kanata
export PATH="$HOME/.cargo/bin:$PATH"

