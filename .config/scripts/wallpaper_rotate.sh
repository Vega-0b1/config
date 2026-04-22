#!/usr/bin/env bash

WALLPAPER_DIR="$HOME/.config/wallpaper"
INTERVAL=900  # 15 minutes in seconds

get_random_wallpaper() {
    find "$WALLPAPER_DIR" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" \) | shuf -n 1
}

set_wallpaper() {
    local wallpaper="$1"
    swww img "$wallpaper" --transition-type wipe --transition-duration 1
}

# Initial wallpaper
set_wallpaper "$(get_random_wallpaper)"

# Rotate every 15 minutes
while true; do
    sleep $INTERVAL
    set_wallpaper "$(get_random_wallpaper)"
done
