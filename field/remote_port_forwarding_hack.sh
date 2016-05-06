OLD_PORTS=0
while : ; do
    PORTS=$(tac ~/screenlog.* | grep -o "Allocated port [0-9]*" -m 2 | cut -d ' '  -f 3)
    echo "got $PORTS"
    if [ "$OLD_PORTS" != "$PORTS" ]
    then
        echo $PORTS | ssh lpng@52.9.177.212   'cat > diagnostic_box_scripts/cloud/ports'
        echo $PORTS | ssh lpng@104.196.19.245 'cat > diagnostic_box_scripts/cloud/ports'
    fi
    OLD_PORTS=$PORTS
    sleep 2
done
