#!/bin/bash

export OMP_NUM_THREADS=1

params_list=(0 1 2 3 4 5 6 7 8 9)
counter_list=(0 1 2 3 4 5 6 7 8 9)

for params in "${params_list[@]}"; do
    for counter in "${counter_list[@]}"; do
        echo "run $params ($counter)"
        nohup python3 evpcd_800_st.py $params &
        nohup python3 evpcd_900_st.py $params &
        nohup python3 evpcd_1000_st.py $params &
        sleep 1
    done
done
