if [ "$#" -ne 1 ]; then
echo "Usage: $0 [hostname]"
exit 1
fi

for PORT in $(cat /home/lpng/diagnostic_box_scripts/cloud/ports); do
echo "Trying to connect to hostname $1 which we expect to be accessable on local port $PORT"
ssh -p $PORT pi@localhost
done
