#!/bin/bash
# tools/umi-usbnet.sh: wait (up to 3 min) for the phone's USB Ethernet to appear after a fastboot boot or a re-plug,
# then give the Mac its address on the link. Run it right after starting the boot, and again after every re-plug
# (macOS makes a new interface each time, often under a new name). It asks for the sudo password once, up front.
# The interface is found by the host MAC the phone's ECM descriptor hands out (02:00:5e:77:ee:01, sweet_usb.c), so
# the name (en8, en9, ...) does not matter; pass a name to force one. Only works while iOS runs (not in TWRP).
WANT=${1:-}
MAC=02:00:5e:77:ee:01
sudo -v || exit 1
find_if() {
	if [ -n "$WANT" ]; then
		ifconfig "$WANT" >/dev/null 2>&1 && echo "$WANT"
		return
	fi
	for i in $(ifconfig -l); do
		ifconfig "$i" 2>/dev/null | grep -qi "ether $MAC" && { echo "$i"; return; }
	done
}
for n in $(seq 1 90); do
	IF=$(find_if)
	if [ -n "$IF" ]; then
		sudo ifconfig "$IF" inet 192.168.7.1 netmask 255.255.255.0 alias && echo "$IF:" && ifconfig "$IF" | grep 'inet 192'
		exit $?
	fi
	sleep 2
done
echo "the phone's USB Ethernet (ether $MAC) did not appear in 3 minutes - is iOS running (not TWRP / fastboot)?" >&2
exit 1
