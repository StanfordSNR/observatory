if [ "$#" -ne 1 ]; then
echo "Usage: $0 [hostname]"
exit 1
fi

ssh -t lpng@104.196.19.245 ./diagnostic_box_scripts/cloud/connect-from-cloud.sh $1
