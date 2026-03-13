# wallpaper-rotator
## Linux and Windows scripts to download and rotate wallpapers.
### The project was created as the Spotlight feature on my Windows 11 installation is not visible as a selection for personalization. I tried all published work arounds but could not fix this. So I figured I could download some wallpapers via a URL and set that as the wall paper. I did not see that my Debian / Gnome OS had this wallpaper rotation option so I wrote similar scripts for Linux as well.
1. On the Linux side, this is a collection of Python and shell scripts which download and set the wallpaper to the Gnome desktop. It uses the "gi" Python interfaces to achieve this. Finally used the crontab to schedule the download and setting of wallpaper.
1. On the Windows side it was a bit more complex. We do not have a straightforward way of setting the wallpaper. After a little bit of research I was able to leverage a COM interface to set the wallpaper. With a Python script to download the wallpapers and an executable to set the wallpaper, it was a matter of having scheduled task to do the magic.
    - The sources Windows version has been created with VS2026 insider version. VS 18.0.
    - The solution can be build from a dev command prompt with the command: ```
    msbuild SetWallpaper.slnx /t:clean;rebuild /p:configuration=Release ```
    - This should create SetWallpaper.exe in the bin/Release folder.
    - You can change the Release to Debug in case you wish to build with debug information.
1. A PowerShell implementation for Windows has also been included here so that it can be used or scheduled without the requirement of having any external software like Python. This script needs the SetWallpaper executable that is mentioned above.