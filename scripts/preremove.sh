#!/bin/sh
set -e

BIN_DIR=/usr/bin
debsystemctl=$(command -v deb-systemd-invoke || echo systemctl)

case "$1" in
	remove|remove-in-favour|deconfigure|deconfigure-in-favour)
		if systemctl is-enabled caddy >/dev/null; then
			echo "Disabling Caddy"
			$debsystemctl stop caddy || exit $?
			systemctl disable caddy || exit $?
			systemctl daemon-reload || true
		fi
		;;

	upgrade|failed-upgrade)
		;;

	*)
		echo "preremove called with unknown argument \`$1'" >&2
		exit 1
		;;
esac

exit 0