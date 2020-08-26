#!/bin/bash
date >> ~/Projects/TimeCsv/daily_wget.log 2>&1
~/Projects/Dropbox-Uploader/dropbox_uploader.sh download Projects/TimeCsv/data/2020_year_2_big_holiday.tcsv ~/Projects/TimeCsv/data/_latest >> ~/Projects/TimeCsv/daily_wget.log 2>&1
echo moving >> ~/Projects/TimeCsv/daily_wget.log 2>&1
mv ~/Projects/TimeCsv/data/_latest ~/Projects/TimeCsv/data/2020_year_2_big_holiday.tcsv >> ~/Projects/TimeCsv/daily_wget.log 2>&1
