#!/bin/sh
set -e

BIN_DIR=/usr/local/bin
debsystemctl=$(command -v deb-systemd-invoke || echo systemctl)

case "$1" in
	abort-upgrade|abort-remove|abort-deconfigure|configure)
		;;
	triggered)
		if [[ "$(readlink /proc/1/exe)" != */systemd ]]; then
			echo "ERROR: systemd not running."
			exit 1
		fi

		systemctl daemon-reload || true

		if systemctl is-enabled caddy >/dev/null; then
			$debsystemctl restart caddy || true
		else
			systemctl enable caddy || true
			$debsystemctl start caddy || true
		fi
		exit 0
		;;
	*)
		echo "postinstall called with unknown argument \`$1'" >&2
		exit 1
		;;
esac

exit 0