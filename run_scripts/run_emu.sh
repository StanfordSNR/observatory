#!/bin/sh

assistant=~/observatory/assistant.py
$assistant --aws-servers -c pkill
$assistant --aws-servers -c setup

console=~/observatory/console.py
no_bbr="default_tcp vegas ledbat pcc verus sprout quic scream webrtc copa taova koho_cc calibrated_koho saturator"
all="bbr $no_bbr"

nohup $console emu --desc 'Calibrated emulator: 2016-12-30T21-38-China-ppp0-to-AWS-Korea-10-runs' --schemes "$all" --run-times 10 --uplink-trace '~/pantheon/test/6.25mbps.trace' --downlink-trace '~/pantheon/test/6.25mbps.trace' --prepend-mm-cmds 'mm-delay 152 mm-loss uplink 0.0025' --extra-mm-link-args '--uplink-queue=droptail --uplink-queue-args=packets=362' aws_korea &
nohup $console emu --desc 'Calibrated emulator: 2017-01-04T07-24-AWS-Brazil-1-to-Brazil-10-runs' --schemes "$all" --run-times 10 --uplink-trace '~/pantheon/test/97.11mbps.trace' --downlink-trace '~/pantheon/test/97.11mbps.trace' --prepend-mm-cmds 'mm-delay 1' --extra-mm-link-args '--uplink-queue=droptail --uplink-queue-args=packets=366' aws_brazil_1 &
nohup $console emu --desc 'Calibrated emulator: 2016-12-30T22-50-AWS-Brazil-2-to-Colombia-ppp0-10-runs' --schemes "$all" --run-times 10 --uplink-trace '~/pantheon/test/5.65mbps.trace' --downlink-trace '~/pantheon/test/5.65mbps.trace' --prepend-mm-cmds 'mm-delay 88 mm-loss uplink 0.0026 mm-loss downlink 0.0001' --extra-mm-link-args '--uplink-queue=droptail --uplink-queue-args=packets=3665' aws_brazil_2 &
nohup $console emu --desc 'Calibrated emulator: 2017-01-02T03-54-India-to-AWS-India-10-runs' --schemes "$all" --run-times 10 --uplink-trace '~/pantheon/test/117.65mbps.trace' --downlink-trace '~/pantheon/test/117.65mbps.trace' --prepend-mm-cmds 'mm-delay 13' --extra-mm-link-args '--uplink-queue=droptail --uplink-queue-args=packets=144' aws_india_1 &
nohup $console emu --desc 'Calibrated emulator: 2017-01-03T21-30-Nepal-to-AWS-India-10-runs' --schemes "$all" --run-times 10 --uplink-trace '~/pantheon/test/13.38mbps.trace' --downlink-trace '~/pantheon/test/13.38mbps.trace' --prepend-mm-cmds 'mm-delay 32 mm-loss uplink 0.003' --extra-mm-link-args '--uplink-queue=droptail --uplink-queue-args=packets=37' aws_india_2 &
