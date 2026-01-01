#!/bin/bash

SCRIPT_NAME=$1
echo -e "Sampling $SCRIPT_NAME"
nohup python3 $SCRIPT_NAME 0 > out_0.log 2>&1 &
nohup python3 $SCRIPT_NAME 1 > out_1.log 2>&1 &
nohup python3 $SCRIPT_NAME 2 > out_2.log 2>&1 &
nohup python3 $SCRIPT_NAME 3 > out_3.log 2>&1 &
