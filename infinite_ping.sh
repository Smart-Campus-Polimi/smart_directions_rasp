#!/bin/bash

mac_address=$1


trap trapint 2

function trapint {
    exit 0
}

echo "ping $mac_address"

while : 
	do
		sudo l2ping $mac_address
done

echo "exit ping process"
#finish