OLD_PORT=0
while : ; do
    PORT=$(cat ~/screenlog.* | grep -o "Allocated port [0-9]*" | tail -n 1 | cut -d ' '  -f 3 | cat)
    echo "got $PORT"
    if [ "$OLD_PORT" != "$PORT" ]
    then
        echo $PORT | ssh lpng@52.9.177.212   'cat > diagnostic_box_scripts/cloud/port'
        echo $PORT | ssh lpng@104.196.19.245 'cat > diagnostic_box_scripts/cloud/port'
    fi
    OLD_PORT=$PORT
    sleep 2
done
