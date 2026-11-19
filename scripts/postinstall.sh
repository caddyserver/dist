#!/bin/sh
set -e

if [ "$1" = "configure" ]; then
	# Add user and group
	if ! getent group caddy >/dev/null; then
		groupadd --system caddy
	fi
	if ! getent passwd caddy >/dev/null; then
		useradd --system \
			--gid caddy \
			--create-home \
			--home-dir /var/lib/caddy \
			--shell /usr/sbin/nologin \
			--comment "Caddy web server" \
			caddy
	fi
	if getent group www-data >/dev/null; then
		usermod -aG www-data caddy
	fi
fi

if [ "$1" = "configure" ] || [ "$1" = "abort-upgrade" ] || [ "$1" = "abort-deconfigure" ] || [ "$1" = "abort-remove" ] ; then
	# This will only remove masks created by d-s-h on package removal.
	deb-systemd-helper unmask caddy.service >/dev/null || true
	deb-systemd-helper unmask caddy-api.service >/dev/null || true

	# was-enabled defaults to true, so new installations run enable.
	if deb-systemd-helper --quiet was-enabled caddy.service; then
		# Enables the unit on first installation, creates new
		# symlinks on upgrades if the unit file has changed.
		deb-systemd-helper enable caddy.service >/dev/null || true
		deb-systemd-invoke start caddy.service >/dev/null || true
	else
		# Update the statefile to add new symlinks (if any), which need to be
		# cleaned up on purge. Also remove old symlinks.
		deb-systemd-helper update-state caddy.service >/dev/null || true
		deb-systemd-helper update-state caddy-api.service >/dev/null || true
	fi

	# Restart only if it was already started
	if [ -d /run/systemd/system ]; then
		systemctl --system daemon-reload >/dev/null || true
		if [ -n "$2" ]; then
			deb-systemd-invoke try-restart caddy.service >/dev/null || true
			deb-systemd-invoke try-restart caddy-api.service >/dev/null || true
		fi
	fi
fi
