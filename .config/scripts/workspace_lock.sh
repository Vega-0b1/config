#!/usr/bin/env bash
# Save and restore workspace for hyprlock

WORKSPACE_FILE="/tmp/hypr_last_workspace"

case "$1" in
    save)
        # Save current workspace before locking
        hyprctl activeworkspace -j | jq -r '.id' > "$WORKSPACE_FILE"
        ;;
    restore)
        # Restore workspace after unlocking
        if [[ -f "$WORKSPACE_FILE" ]]; then
            workspace=$(cat "$WORKSPACE_FILE")
            hyprctl dispatch workspace "$workspace"
            rm "$WORKSPACE_FILE"
        fi
        ;;
    *)
        echo "Usage: $0 {save|restore}"
        exit 1
        ;;
esac
