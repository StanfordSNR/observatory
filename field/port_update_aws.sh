#! /bin/bash

cd /tmp/aws_logs
AWS_ADDRESS=lpng@52.192.246.2

OLD_PORT=0
while : ; do
    PORT=$(tac autossh_aws.log | grep -o "Allocated port [0-9]*" -m 1 | cut -d ' ' -f 3)
    if [ "$OLD_PORT" != "$PORT" ]
    then
        ssh $AWS_ADDRESS "set_port --port $PORT"
    fi
    OLD_PORT=$PORT
    sleep 1
done
