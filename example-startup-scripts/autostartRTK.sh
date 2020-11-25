#!/bin/bash

export LOGFILE=/home/attrac/autostartRTK.log

cd /pubfiles/github/mfassler/python3-rtcm3

while true
do
    echo >>$LOGFILE
    echo "----------------------------------------------" >> $LOGFILE
    date >> $LOGFILE

    echo "Starting RTK/NTRIP service..." >> $LOGFILE

	python3 rx_on_ntrip_commercial.py  &>>$LOGFILE

    echo "... ntrip seems to have stopped." >> $LOGFILE

    date >> $LOGFILE
	sleep 1

done

