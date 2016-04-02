if [ "$#" -ne 2 ]; then
echo "Usage: $0 [username] [hostname]"
exit 1
fi
PORT=`./hostname-to-port.sh $2`
echo "Trying to connect to hostname $1 which we expect to be accessable on local port $PORT"
ssh -p $PORT $1@localhost
