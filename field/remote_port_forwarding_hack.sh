cat ~/screen.* | grep port | tail -n 1 | tr -d -c 1-9 | echo
