echo -n "got "
cat ~/screenlog.* | grep "Allocated port" | tail -n 1 | cut -d ' '  -f 3 | cat
cat ~/screenlog.* | grep "Allocated port" | tail -n 1 | cut -d ' '  -f 3 | ssh lpng@52.9.177.212 'cat > diagnostic_box_scripts/cloud/port'
cat ~/screenlog.* | grep "Allocated port" | tail -n 1 | cut -d ' '  -f 3 | ssh lpng@104.196.19.245 'cat > diagnostic_box_scripts/cloud/port'
