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

# Display brightness level with Wofi
echo "🔆 Brightness: $PERCENTAGE%" | wofi --dmenu --lines=1 --width=200
