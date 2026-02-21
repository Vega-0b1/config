#!/usr/bin/env bash

WALLPAPER_DIR="$HOME/.config/wallpaper"
INTERVAL=900  # 15 minutes in seconds

get_random_wallpaper() {
    find "$WALLPAPER_DIR" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" \) | shuf -n 1
}

set_wallpaper() {
    local wallpaper="$1"

    # Get all monitors
    monitors=$(hyprctl monitors | grep "Monitor" | awk '{print $2}')

    # Preload new wallpaper
    hyprctl hyprpaper preload "$wallpaper"

    # Set wallpaper on all monitors
    for monitor in $monitors; do
        hyprctl hyprpaper wallpaper "$monitor,$wallpaper"
    done

    # Unload unused wallpapers to free memory
    hyprctl hyprpaper unload all
}

# Initial wallpaper
set_wallpaper "$(get_random_wallpaper)"

# Rotate every 15 minutes
while true; do
    sleep $INTERVAL
    set_wallpaper "$(get_random_wallpaper)"
done
