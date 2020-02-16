#!/bin/bash

systemctl daemon-reload

systemctl enable fail2ban
systemctl start fail2ban

systemctl enable caddy
systemctl start caddy

systemctl enable ufw
systemctl start ufw