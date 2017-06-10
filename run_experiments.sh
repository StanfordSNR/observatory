#!/bin/sh

assistent=~/observatory/assistent.py
nohup $assistent --all pkill

console=~/observatory/console.py
no_bbr="default_tcp vegas ledbat pcc verus sprout quic scream webrtc copa taova koho_cc calibrated_koho saturator"
all="$no_bbr bbr"

nohup $console --schemes "$all" --run-times 10 aws_california_1 stanford &
nohup $console --schemes "$all" --run-times 10 aws_california_2 mexico &
nohup $console --schemes "$all" --run-times 10 aws_brazil_1 brazil &
nohup $console --schemes "$all" --run-times 10 aws_brazil_2 colombia &
nohup $console --schemes "$all" --run-times 10 aws_india_1 india &
nohup $console --schemes "$all" --run-times 10 aws_korea china &
nohup $console --schemes "$no_bbr" --run-times 10 aws_india_2 nepal &
