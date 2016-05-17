if [ "$#" -ne 1 ]; then
echo "Usage: $0 [hostname]"
exit 1
fi

ssh -t lpng@52.192.246.2 ./diagnostic_box_scripts/cloud/connect_from_cloud.sh $1
