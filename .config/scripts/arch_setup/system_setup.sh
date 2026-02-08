systemctl enable --now bluetooth
systemctl set-default graphical.target
systemctl enable --now sddm.service

systemctl status bluetooth graphical.target sddm.service | cat
