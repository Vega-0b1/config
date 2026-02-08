
#!/usr/bin/env bash

set -euo pipefail

ACTION="${1:-}"  # up | down
if [[ "$ACTION" != "up" && "$ACTION" != "down" ]]; then
  echo "Usage: $0 {up|down}" >&2
  exit 1
fi

# Prefer the real backlight class if available
DEVICE_OPT=""
if brightnessctl -l | grep -q '\bbacklight\b'; then
  DEVICE_OPT="-c backlight"
fi

get_pct() {
  local cur max
  cur="$(brightnessctl $DEVICE_OPT get)"
  max="$(brightnessctl $DEVICE_OPT max)"
  if [[ "$max" -eq 0 ]]; then echo 0; else echo $(( cur * 100 / max )); fi
}

pct_before="$(get_pct)"

# Compute absolute target percentage with snapping rules
target="$pct_before"
if [[ "$ACTION" == "down" ]]; then
  if (( pct_before <= 5 )); then
    # Bottom zone: 1% steps down, clamp at 0
    target=$(( pct_before - 1 ))
    (( target < 0 )) && target=0
  else
    # Above 5: snap down to 5% grid
    # if already multiple of 5 -> minus 5; else floor to nearest multiple of 5
    if (( pct_before % 5 == 0 )); then
      target=$(( pct_before - 5 ))
    else
      target=$(( (pct_before / 5) * 5 ))
    fi
  fi
else # ACTION == up
  if (( pct_before < 5 )); then
    # Bottom zone: 1% steps up (but don't overshoot 5 suddenly)
    target=$(( pct_before + 1 ))
  elif (( pct_before == 5 )); then
    # At 5 and going up -> jump to 10 to enter the 5% grid cleanly
    target=10
  else
    # Above 5: snap up to next 5% multiple
    if (( pct_before % 5 == 0 )); then
      target=$(( pct_before + 5 ))
    else
      target=$(( ((pct_before + 4) / 5) * 5 ))  # ceil to next multiple of 5
    fi
  fi
  (( target > 100 )) && target=100
fi

# Apply absolute brightness safely
brightnessctl $DEVICE_OPT -q set "${target}%"

pct_after="$(get_pct)"

# Build a tiny 10-step bar for the OSD
steps=10
filled=$(( pct_after * steps / 100 ))
bar="$(printf '█%.0s' $(seq 1 $filled))$(printf '░%.0s' $(seq 1 $((steps - filled))))"

notify-send -a "brightness" -r 9991 -t 1200 \
  -h "string:x-canonical-private-synchronous:brightness" \
  -h "int:value:${pct_after}" \
  "Brightness ${pct_after}%" "$bar" \
  -i display-brightness-symbolic
