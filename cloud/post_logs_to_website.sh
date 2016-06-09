cd ~/diagnostic_box_scripts/cloud/status_logs
while : ; do
    sleep 5s
    for l in *
        do
            echo $l
            touch ../uploaded_status_logs/$l
            comm -23 $l ../uploaded_status_logs/$l > /tmp/toUpload

            while read line; do
                HOSTNAME=$l
                POST_REQ='hostname='$l'&datetime='$(echo $line | sed 's/\ diagnostic_box_scripts\ HEAD=/\&head=/g; s/\ temp=/\&temp=/g; s/C$//g')
                curl -i -X POST -d "$POST_REQ" https://network-observatory.herokuapp.com/post-measurement-box-checkin
            done < /tmp/toUpload

            mv /tmp/toUpload ../uploaded_status_logs/$l
        done
done
