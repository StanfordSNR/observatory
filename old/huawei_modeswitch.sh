#!/bin/sh

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <product-ID>"
  exit 1
fi

/usr/sbin/usb_modeswitch -v 0x12d1 -p 0x$1 -W -R -M \
  55534243123456780000000000000011062000000100010100000000000000
