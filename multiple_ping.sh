#!/bin/bash

ARRAY_MAC=("$@")

if [ ${#ARRAY_MAC[*]} -eq 0 ]; then
    echo "Oops, something went wrong... No MAC ADDRESSES specified"
else
    pos=$(( ${#ARRAY_MAC[*]} - 1 ))
	last=${ARRAY_MAC[$pos]}
	echo "Ping ${ARRAY_MAC[*]} ..."
fi


for mac in ${ARRAY_MAC[*]}
do
	if [[ $mac == $last ]]
	then 
		until l2ping $mac; do 
			sleep 1
		done
		break
	fi


	until l2ping $mac; do 
		sleep 1
	done &

done

echo "exit ping process"
#finish