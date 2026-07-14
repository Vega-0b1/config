#!/usr/bin/env bash
# Arch Linux setup script — mirrors NixOS config at github.com/Vega-0b1/nix-config
# Run as regular user on a fresh EndeavourOS CLI install. Safe to rerun.

set -euo pipefail

DOTFILES_REPO="https://github.com/Vega-0b1/config"
DOTFILES_DIR="$HOME/config"

# ──────────────────────────────────────────────────────────────────────────────
detect_gpu() {
  echo "==> Detecting GPU..."
  if lspci 2>/dev/null | grep -qiE 'amdgpu|radeon|AMD.*VGA|AMD.*Display'; then
    GPU_VENDOR=amd
  elif lspci 2>/dev/null | grep -qiE 'Intel.*Graphics|Intel.*VGA|Intel.*Display'; then
    GPU_VENDOR=intel
  elif lspci 2>/dev/null | grep -qi 'NVIDIA'; then
    GPU_VENDOR=nvidia
  else
    echo "Could not auto-detect GPU. Please select:"
    select v in amd intel nvidia; do GPU_VENDOR=$v; break; done
  fi
  echo "    GPU: $GPU_VENDOR"
}

# ──────────────────────────────────────────────────────────────────────────────
install_packages_pacman() {
  echo "==> Installing pacman packages..."
  sudo pacman -Syu --needed --noconfirm \
    neovim git wget curl jq htop ripgrep fd git-delta shfmt brightnessctl \
    hyprland waybar mako rofi wl-clipboard hyprlock hypridle \
    uwsm wl-clip-persist hyprpolkitagent \
    pipewire pipewire-alsa pipewire-pulse wireplumber rtkit pavucontrol \
    sddm networkmanager network-manager-applet \
    firefox alacritty mpv playerctl \
    gcc rust rust-analyzer python python-numpy python-black \
    kotlin clang lua-language-server pyright \
    bash-language-server typescript-language-server \
    prettier typescript stylua \
    noto-fonts papirus-icon-theme ttf-meslo-nerd ttf-firacode-nerd \
    udisks2 gvfs gvfs-smb gnome-keyring libsecret \
    openssh tailscale \
    cups avahi nss-mdns \
    libvirt qemu-full virt-manager \
    steam gamemode lib32-gamemode \
    acpi powertop sox iperf3 psmisc poppler \
    file-roller nemo 7zip libva-utils mesa-demos \
    power-profiles-daemon \
    xdg-user-dirs xdg-utils libnotify wpa_supplicant \
    qbittorrent libreoffice-fresh freecad nextcloud-client \
    grimblast

  # GPU-specific packages
  if [[ "$GPU_VENDOR" == "intel" ]]; then
    sudo pacman -S --needed --noconfirm intel-media-driver libinput
  fi
}

# ──────────────────────────────────────────────────────────────────────────────
install_packages_aur() {
  echo "==> Installing AUR packages..."

  # Ensure yay is available
  if ! command -v yay &>/dev/null; then
    echo "    Installing yay..."
    local tmp=$(mktemp -d)
    git clone https://aur.archlinux.org/yay-bin.git "$tmp/yay-bin"
    (cd "$tmp/yay-bin" && makepkg -si --noconfirm)
    rm -rf "$tmp"
  fi

  yay -S --needed --noconfirm \
    brave-bin nanum-fonts \
    adw-gtk3 rose-pine-hyprcursor sddm-astronaut-theme \
    swww hypr-relay-git rofi-bluetooth-git kanata \
    jdtls kotlin-language-server \
    vscode-langservers-extracted \
    google-java-format htmlhint \
    live-server \
    claude-code streamrip \
    orca-slicer zoom \
    ryubing citron-emu-git python-platformio stm32cubemx

  # GPU-specific AUR packages
  if [[ "$GPU_VENDOR" == "intel" ]]; then
    yay -S --needed --noconfirm vpl-gpu-rt
  fi
}

# ──────────────────────────────────────────────────────────────────────────────
enable_services() {
  echo "==> Enabling system services..."
  sudo systemctl enable --now NetworkManager
  sudo systemctl enable --now rtkit-daemon
  sudo systemctl enable --now sddm
  sudo systemctl enable --now openssh
  sudo systemctl enable --now tailscaled
  sudo systemctl enable --now udisks2
  sudo systemctl enable --now avahi-daemon
  sudo systemctl enable --now cups
  sudo systemctl enable --now libvirtd
  sudo systemctl enable --now power-profiles-daemon
  sudo systemctl enable --now bluetooth

  echo "==> Enabling user services..."
  systemctl --user enable --now pipewire pipewire-pulse wireplumber

  echo "==> Enabling kanata..."
  sudo systemctl enable --now kanata

  echo "==> Configuring groups..."
  sudo usermod -aG input,uinput,libvirt,audio,wheel,networkmanager,dialout "$USER"

  echo "==> Configuring PAM for gnome-keyring..."
  local pam_login=/etc/pam.d/login
  if ! grep -q pam_gnome_keyring "$pam_login" 2>/dev/null; then
    sudo tee -a "$pam_login" > /dev/null <<'EOF'
auth     optional  pam_gnome_keyring.so
session  optional  pam_gnome_keyring.so auto_start
EOF
  fi
}

# ──────────────────────────────────────────────────────────────────────────────
configure_system() {
  echo "==> Writing system-level configs..."

  # Kanata
  sudo mkdir -p /etc/kanata
  sudo cp "$DOTFILES_DIR/.config/kanata/kanata.kbd" /etc/kanata/kanata.kbd

  # Kanata systemd service (detects keyboard paths; add your device to the list)
  sudo tee /etc/systemd/system/kanata.service > /dev/null <<'EOF'
[Unit]
Description=Kanata key remapper
After=local-fs.target

[Service]
Type=simple
ExecStart=/usr/bin/kanata --cfg /etc/kanata/kanata.kbd
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
  sudo systemctl daemon-reload
  sudo systemctl enable --now kanata

  # SDDM theme
  sudo mkdir -p /etc/sddm.conf.d
  sudo tee /etc/sddm.conf.d/theme.conf > /dev/null <<'EOF'
[Theme]
Current=sddm-astronaut-theme
EOF

  # Set timezone and locale
  sudo timedatectl set-timezone America/Los_Angeles
  sudo localectl set-locale LANG=en_US.UTF-8

  # dconf / gsettings for GTK theming
  if command -v gsettings &>/dev/null; then
    gsettings set org.gnome.desktop.interface color-scheme prefer-dark
    gsettings set org.gnome.desktop.interface icon-theme Papirus-Dark
    gsettings set org.gnome.desktop.interface monospace-font-name "FiraCode Nerd Font Mono 12"
    gsettings set org.gnome.desktop.interface text-scaling-factor 1.0
  fi

  # Lid switch handling (for laptops)
  sudo mkdir -p /etc/systemd/logind.conf.d
  sudo tee /etc/systemd/logind.conf.d/lid.conf > /dev/null <<'EOF'
[Login]
HandleLidSwitch=hibernate
HandleLidSwitchExternalPower=hibernate
HandleLidSwitchDocked=ignore
EOF
}

# ──────────────────────────────────────────────────────────────────────────────
deploy_dotfiles() {
  echo "==> Deploying dotfiles from $DOTFILES_REPO..."

  if [ -d "$DOTFILES_DIR/.git" ]; then
    git -C "$DOTFILES_DIR" pull
  else
    git clone "$DOTFILES_REPO" "$DOTFILES_DIR"
  fi

  mkdir -p "$HOME/.config"
  cp -r "$DOTFILES_DIR/.config/." "$HOME/.config/"

  [ -f "$DOTFILES_DIR/.bashrc"    ] && cp "$DOTFILES_DIR/.bashrc"    "$HOME/.bashrc"
  [ -f "$DOTFILES_DIR/.gitconfig" ] && cp "$DOTFILES_DIR/.gitconfig" "$HOME/.gitconfig"

  # Make scripts executable
  chmod +x "$HOME/.config/scripts/"*.sh 2>/dev/null || true

  # Enable user systemd units from dotfiles
  systemctl --user daemon-reload
  systemctl --user enable --now clock-chime.timer

  # Create wallpaper directory
  mkdir -p "$HOME/Pictures/wallpapers"
  echo "    Note: add wallpapers to ~/Pictures/wallpapers/"
}

# ──────────────────────────────────────────────────────────────────────────────
post_install_notes() {
  cat <<'EOF'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Setup complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next steps:
  1. Reboot  →  SDDM should show the astronaut/black_hole theme
  2. Log in  →  Hyprland via UWSM
  3. SUPER+RETURN opens Alacritty
  4. SUPER+/      opens Rofi launcher
  5. Open nvim    →  lazy.nvim installs plugins on first launch
                      run :checkhealth to verify LSPs

VM note:
  If Hyprland fails to start due to GPU, add to ~/.config/uwsm/env:
    export WLR_RENDERER_ALLOW_SOFTWARE=1

Kanata devices:
  Edit /etc/kanata/kanata.kbd and add your keyboard paths
  to the defcfg block if the default paths don't match.

EOF
}

# ──────────────────────────────────────────────────────────────────────────────
main() {
  detect_gpu
  install_packages_pacman
  install_packages_aur
  enable_services
  configure_system
  deploy_dotfiles
  post_install_notes
}

main
