if [ "$#" -ne 2 ]; then
echo "Usage: $0 [username] [port]"
exit 1
fi
echo "Trying to connect to hostname $1 which we expect to be accessable on local port $2"
ssh -p $2 $1@localhost
