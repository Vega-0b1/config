wallpaper_path='/home/jcvega/.config/sway/wallpaper'

random_wallpaper=$(find '$wallpaper_path' type f | shuf -n 1)

swaymsg output * background '$random_wallpaper' fill
