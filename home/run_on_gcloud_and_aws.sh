if [ "$#" -ne 1 ]; then
echo "Usage: $0 [command]"
exit 1
fi

ssh -t lpng@52.192.246.2 $1
ssh -t lpng@23.251.141.221 $1
