if [ "$#" -ne 1 ]; then
echo "Usage: $0 [hostname]"
exit 1
fi

PORT=$(cat /home/lpng/diagnostic_box_scripts/cloud/dynamic_ports/$1 2> /dev/null )
if [ $PORT ]; then
    echo "Trying to connect to hostname $1 which we expect to be accessible on local port $PORT"
    ssh -p $PORT pi@localhost
else
    echo "Can't connect to hostname $1"
fi
