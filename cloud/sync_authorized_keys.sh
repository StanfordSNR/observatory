cd diagnostic_box_scripts; git pull --ff-only;
sort -u ~/.ssh/authorized_keys ~/diagnostic_box_scripts/field/initialization/authorized_keys > /tmp/authorized_keys;
mv /tmp/authorized_keys ~/.ssh/authorized_keys;
echo keys synced
