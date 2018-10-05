#!/bin/bash

mac_address=$1


trap trapint 2

function trapint {
    exit 0
}

while : 
	do
		sudo l2ping -s 1 -f $mac_address
done

echo "exit ping process"
#finish
