if [ "$#" -ne 2 ]; then
echo "Usage: $0 [username] [hostname]"
exit 1
fi

ssh -t lpng@104.196.19.245 ./diagnostic_box_scripts/connect-from-cloud.sh $1 $2
