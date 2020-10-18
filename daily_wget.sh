#!/bin/bash
PROJECT=TimeCsv
FOLDER=~/Projects/$PROJECT
FILENAME="2021_year_3_semester_1.tcsv"
LOG=$FOLDER/daily_wget.log
LOG_NEW=$FOLDER/daily_wget.log.new
TEMP_LOCATION=$FOLDER/data/_latest

date > $LOG_NEW 2>&1
~/Projects/Dropbox-Uploader/dropbox_uploader.sh download Projects/$PROJECT/data/$FILENAME $TEMP_LOCATION >> $LOG_NEW 2>&1
echo moving $FILENAME >> $LOG_NEW 2>&1
mv $TEMP_LOCATION $FOLDER/data/$FILENAME >> $LOG_NEW 2>&1
cat $LOG_NEW >> $LOG
