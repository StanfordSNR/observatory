if [ "$#" -ne 1 ]; then
echo "Usage: $0 [hostname]"
exit 1
fi

PORT=$(/home/lpng/diagnostic_box_scripts/field/machine_to_port.py $1)
echo "Trying to connect to hostname $1 which we expect to be accessable on local port $PORT"
ssh -p $PORT pi@localhost
