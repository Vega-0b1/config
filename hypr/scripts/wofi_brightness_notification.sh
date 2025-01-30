#!/bin/bash

# Adjust brightness
if [[ "$1" == "up" ]]; then
    brightnessctl set +5%
elif [[ "$1" == "down" ]]; then
    brightnessctl set 5%-
fi

# Get the current brightness level
BRIGHTNESS=$(brightnessctl get)
MAX_BRIGHTNESS=$(brightnessctl max)
PERCENTAGE=$((BRIGHTNESS * 100 / MAX_BRIGHTNESS))

# Create the brightness message
MESSAGE="  🔆 Brightness: $PERCENTAGE"

# Use the notification-specific Wofi config and style
echo "$MESSAGE" | wofi --dmenu --conf ~/.config/wofi/notifications/config --height 8% --width 10% --style ~/.config/wofi/notifications/volume.css &
WOFI_PID=$!

# Close Wofi after 2 seconds
sleep 1
kill "$WOFI_PID" 2>/dev/null
