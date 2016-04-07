if [ "$#" -ne 2 ]; then
echo "Usage: $0 [username] [hostname]"
exit 1
fi

# choose port between 2000, 65499 based on the first 64 bits of the md5sum of the case-insensitive hostname (63499 is a prime number)
PORT=$(( (0x`tr "[:upper:]" "[:lower:]" <<< $HOSTNAME | md5sum | cut -c -16` % 63499) + 2000 ))

echo "Trying to connect to hostname $2 which we expect to be accessable on local port $PORT"
ssh $1@localhost:$PORT
