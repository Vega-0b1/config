#!/bin/bash

# Get the current bar mode
current_mode=$(swaymsg -t get_bar_config bar-0 | jq -r '.mode')

# Toggle the mode
if [ "$current_mode" == "hide" ]; then
  swaymsg bar mode dock
elif [ "$current_mode" == "dock" ]; then
  swaymsg bar mode hide
else
  echo "Bar is in an unsupported mode: $current_mode"
fi
