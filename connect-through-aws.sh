if [ "$#" -ne 2 ]; then
echo "Usage: $0 [username] [hostname]"
exit 1
fi

ssh lpng@52.9.177.212 ./diagnostic_box_scripts/connect-from-cloud.sh $1 $2
