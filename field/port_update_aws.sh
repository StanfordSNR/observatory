#! /bin/bash -x

# ssh -R prints locally which port it is bound to on the remote machine. This script gets this port number from the log for the autossh script and gives it to the cloud server.

cd /tmp/
AWS_ADDRESS=lpng@52.192.246.2

OLD_PORT=0
while : ; do
    PORT=$(tac autossh_aws.log | grep -o "Allocated port [0-9]*" -m 1 | cut -d ' ' -f 3)
    if [ "$OLD_PORT" != "$PORT" ] # if port has changed from the last one we updated
    then
        ssh $AWS_ADDRESS "set_port --port $PORT"
    fi
    OLD_PORT=$PORT
    sleep 5
done
