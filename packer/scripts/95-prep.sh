#!/bin/bash


rm /var/log/*.log
rm -rf /var/log/unattended-upgrades
rm -rf /root/.ansible

# the 90-clean.sh script from https://github.com/digitalocean/marketplace-partners
# deletes this file, which locks users out. Re-create it.
touch /etc/ssh/revoked_keys
