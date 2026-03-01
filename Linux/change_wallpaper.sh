#!/bin/bash
echo Date is $(date) >> ~/change_wallpaper.log
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"
/usr/bin/python3 /usr/bin/download_n_set_wallpaper.py >> ~/change_wpaper.log
