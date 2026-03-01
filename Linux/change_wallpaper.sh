#!/bin/bash
# We will create a log file in the user's home directory to keep track of
#  when the wallpaper was changed and any output from the Python script.
echo Date is $(date) >> ~/change_wallpaper.log
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"
/usr/bin/python3 /usr/bin/download_n_set_wallpaper.py >> ~/change_wallpaper.log
#-----------
# This script is intended to be run as a cron job. To set it up, you can use the following command:
# crontab -e
# Then add the following line to run the script every hour:
# 0 * * * * USERLOGIN /path/to/change_wallpaper.sh
# Make sure to replace /path/to/change_wallpaper.sh with the actual path to your script,
#  and USERLOGIN with your actual username.
# Also, ensure that the script has execute permissions:
#  chmod +x /path/to/change_wallpaper.sh