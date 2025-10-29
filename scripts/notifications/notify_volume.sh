
#!/usr/bin/env bash
# Minimal volume OSD (10% steps) for PipeWire/wpctl + mako

set -euo pipefail

ACTION="${1:-}"                          # up | down | mute
SINK="${SINK:-@DEFAULT_AUDIO_SINK@}"     # override with: SINK=... volume-osd up

if [[ "$ACTION" != "up" && "$ACTION" != "down" && "$ACTION" != "mute" ]]; then
  echo "Usage: $0 {up|down|mute}" >&2
  exit 1
fi

# Apply change
case "$ACTION" in
  up)   wpctl set-mute "$SINK" 0; wpctl set-volume "$SINK" 10%+ --limit 1.0 ;;
  down) wpctl set-mute "$SINK" 0; wpctl set-volume "$SINK" 10%- ;;
  mute) wpctl set-mute "$SINK" toggle ;;
esac

# Read state
out="$(wpctl get-volume "$SINK" || true)"      # "Volume: 0.60 [MUTED]"
volf="$(awk '{print $2}' <<<"$out")"; [[ -z "${volf:-}" ]] && volf="0"
pct="$(awk -v v="$volf" 'BEGIN{printf("%.0f", v*100)}')"
muted=0; grep -q '\[MUTED\]' <<<"$out" && muted=1

# Icon + bar
if (( muted==1 || pct==0 )); then
  icon="audio-volume-muted-symbolic"
elif (( pct < 34 )); then
  icon="audio-volume-low-symbolic"
elif (( pct < 67 )); then
  icon="audio-volume-medium-symbolic"
else
  icon="audio-volume-high-symbolic"
fi

filled=$(( pct / 10 ))
bar="$(printf '█%.0s' $(seq 1 $filled))$(printf '░%.0s' $(seq 1 $((10 - filled))))"
title=$([[ "$muted" -eq 1 ]] && echo "Volume (muted)" || echo "Volume ${pct}%")

notify-send -a "volume" -r 9990 -t 1200 \
  -h "string:x-canonical-private-synchronous:volume" \
  -h "int:value:${pct}" \
  "$title" "$bar" -i "$icon" || true
