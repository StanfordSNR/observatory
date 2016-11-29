#!/bin/sh -x

echo 0 | sudo tee /proc/sys/net/ipv4/conf/all/rp_filter
echo 0 | sudo tee /proc/sys/net/ipv4/conf/ppp0/rp_filter
