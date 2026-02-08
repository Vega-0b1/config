cp /home/jcvega/.config/scripts/arch_setup/kanata.service /etc/systemd/system
systemctl daemon-reload
systemctl enable --now kanata.service
