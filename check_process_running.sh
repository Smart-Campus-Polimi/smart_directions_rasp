#!/bin/bash

my_cmd=$1

ps cax | grep $my_cmd | grep -o '^[ ]*[0-9]*' |tr '\n' ' '


#if [ $? -eq 0 ]; then
#	echo "Process is running."
#else
#	echo "Process is not running."
#fi