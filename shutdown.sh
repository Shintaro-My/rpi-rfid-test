#!/bin/bash

for i in {1..5}
do
    sudo -H -u pi python3 shutdown.py
    if [ $? -eq 0 ]; then
        echo "Success"
        break
    else
        sleep 5
    fi
done

if [ $i -eq 5 ]; then
    echo "Retry failed"
fi