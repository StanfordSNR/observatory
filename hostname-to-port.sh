if [ "$#" -ne 1 ]; then
echo "Usage: $0 [hostname]"
exit -1
fi

PRIME=61991 # large prime
MD5=`echo -n $1 | tr "[:upper:]" "[:lower:]" | md5sum`
echo -n $(( $(( 0x${MD5:0:7} % $PRIME )) + 2000 ))
