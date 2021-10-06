#!/bin/bash
PROJECT=TimeCsv
FOLDER=~/Projects/$PROJECT
LOG_FOLDER=$FOLDER/Telegram_Bot/Logs
LOG=$LOG_FOLDER/daily_wget.log
LOG_NEW=$LOG_FOLDER/daily_wget.log.new
TEMP_LOCATION=$FOLDER/data/_latest


# Declare a string array with type
declare -a FileNameArray=(
	"University/2019_year_1_big_holiday.tcsv"
	"University/2019_year_1_semester_2_exams.tcsv"
	"University/2020_year_2_big_holiday.tcsv"
	"University/2020_year_2_semester_1_exams.tcsv"
	"University/2020_year_2_semester_1.tcsv"
	"University/2020_year_2_semester_2.tcsv"
	"University/2020_year_2_small_holiday.tcsv"
	"University/2021_year_3_semester_1.tcsv"
	"University/2021_year_3_semester_2.tcsv"
	"University/2021_year_3_small_holiday.tcsv"
	"University/2021_year_3_big_holiday.tcsv"
	"Work/2021_classiq.tcsv"
)

date > $LOG_NEW 2>&1

for FILENAME in "${FileNameArray[@]}"; do
  echo $FILENAME
  ~/Projects/Dropbox-Uploader/dropbox_uploader.sh download Projects/$PROJECT/data/$FILENAME $TEMP_LOCATION >> $LOG_NEW 2>&1
  echo moving $FILENAME >> $LOG_NEW 2>&1
  mv $TEMP_LOCATION $FOLDER/data/$FILENAME >> $LOG_NEW 2>&1
done

cat $LOG_NEW >> $LOG
