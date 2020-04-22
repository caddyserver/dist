#!/bin/sh
set -e

BIN_DIR=/usr/bin
debsystemctl=$(command -v deb-systemd-invoke || echo systemctl)

case "$1" in
	abort-upgrade|abort-remove|abort-deconfigure|triggered)
		;;
	configure)
		case "$(readlink /proc/1/exe)" in
			*/systemd) ;;
			*) echo "ERROR: systemd not running." && exit 1
		esac

		systemctl daemon-reload || true

		if systemctl is-enabled caddy >/dev/null; then
			echo "Restarting Caddy..."
			$debsystemctl restart caddy || echo "WARNING: failed to restart Caddy"
		else
			echo "Starting Caddy..."
			systemctl enable caddy || true
			$debsystemctl start caddy || echo "WARNING: failed to start Caddy"
		fi
		exit 0
		;;
	*)
		echo "postinstall called with unknown argument \`$1'" >&2
		exit 1
		;;
esac

exit 0