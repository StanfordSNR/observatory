#!/bin/sh
IPADDR=$1
TOKEN=$(curl http://${IPADDR}/api/webserver/token|xmllint –xpath ‘//response/token/text()’ -)
curl -X POST -H “__RequestVerificationToken:${TOKEN}” -H “Content-type: text/xml” -d “1” http://${IPADDR}/api/device/mode
