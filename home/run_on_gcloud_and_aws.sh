if [ "$#" -ne 1 ]; then
echo "Usage: $0 [command]"
exit 1
fi

ssh lpng@52.9.177.212 $1
ssh lpng@104.196.19.245 $1
