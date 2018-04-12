#! /bin/bash

MAC=$1
remove="RSSI return value: "
sum_rssi=0
x=0

echo "start pinging $MAC"

while true; do
	((x++))
	OUT="$(sudo hcitool rssi $MAC)"
	RSSI_val=${OUT#$remove}
	sum_rssi=$((sum_rssi+RSSI_val))
	avg=$((sum_rssi/x))
	if [ $x -eq 50 ]; then
		echo "$avg"
		x=0
		sum_rssi=0
	fi
	#echo "rssi: $RSSI_val  ----- avg rssi: $avg"
done

