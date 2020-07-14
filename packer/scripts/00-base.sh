#!/bin/bash

apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y -q
apt install -y unattended-upgrades fail2ban
apt autoremove -y
apt autoclean -y
