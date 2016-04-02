if [ "$#" -ne 2 ]; then
echo "Usage: $0 [username] [hostname]"
exit 1
fi
PORT=$(( (0x`tr "[:upper:]" "[:lower:]" <<< $2 | md5sum | cut -c -8` % 61991) + 2000 )) # 2000 min port, 61991 random prime
echo "Trying to connect to hostname $1 which we expect to be accessable on local port $PORT"
ssh -p $PORT $1@localhost
