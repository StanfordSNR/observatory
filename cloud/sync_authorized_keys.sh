git pull --ff-only;
sort -u ~/.ssh/authorized_keys ~/diagnostic_box_scripts/field/authorized_keys > /tmp/authorized_keys;
mv /tmp/authorized_keys ~/.ssh/authorized_keys;
echo keys synced
