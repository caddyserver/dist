#!/bin/bash

apt update -y
apt dist-upgrade -y
apt install -y unattended-upgrades fail2ban
apt autoremove -y
apt autoclean -y
