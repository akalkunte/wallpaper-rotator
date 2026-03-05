using System;
using System.IO;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text;
// This code is based on the IDesktopWallpaper interface, which is used to manage desktop wallpapers in Windows.
// The code defines a class called WallpaperDetails that provides methods to set the wallpaper for all monitors
// and to retrieve details about the current wallpaper configuration.
// The class uses COM interop to interact with the IDesktopWallpaper interface, allowing it to set and get wallpaper
// information for multiple monitors.
namespace WindowsWallpaper
{
    internal class WallpaperDetails
    {
        [StructLayout(LayoutKind.Sequential)]
        public struct RECT
        {
            public int Left, Top, Right, Bottom;
        }
        // Specifies how the desktop wallpaper should be displayed.
        [ComVisible(true)]
        public enum DESKTOP_WALLPAPER_POSITION
        {
            
            DWPOS_CENTER = 0, // Center the image, no resize.
            DWPOS_TILE = 1, // Tile across all monitors.
            DWPOS_STRETCH = 2, // Stretch to fit.
            // Stretch image to fit the height or width of the monitor, WITHOUT changing aspect ratio or cropping
            // Can result in colored spaces on sides of the image.
            DWPOS_FIT = 3,
            DWPOS_FILL = 4, // Stretch the image to fill the screen
            DWPOS_SPAN = 5 // Single image spans across all monitors.
        }
        // The direction that the slideshow should advance.
        [ComVisible(true)]
        public enum DESKTOP_SLIDESHOW_DIRECTION
        {
            DSD_FORWARD = 0,
            DSD_BACKWARD = 1
        }
        [ComVisible(true)]
        [Flags]
        public enum DESKTOP_SLIDESHOW_STATE
        {
            DSS_ENABLED = 1, // Enabled.
            DSS_SLIDESHOW = 2, // Currently configured.
            DSS_DISABLED_BY_REMOTE_SESSION = 4 // Disabled by a remote session.
        }
        [ComImport]
        [Guid("B92B56A9-8B55-4E14-9A89-0199BBB6F93B")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        public interface IDesktopWallpaper
        {
            // **** Method ordering is absolutely critical to the functioning of the interface.
            // **** The following code ordering below MUST be maintained.
            // **** Not doing so will result in an AccessViolationException being thrown.

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            void SetWallpaper([MarshalAs(UnmanagedType.LPWStr)] string monitorID, [MarshalAs(UnmanagedType.LPWStr)] string wallpaper);

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            [return: MarshalAs(UnmanagedType.LPWStr)]
            StringBuilder GetWallpaper([MarshalAs(UnmanagedType.LPWStr)] string monitorID);

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            [return: MarshalAs(UnmanagedType.LPWStr)]
            StringBuilder GetMonitorDevicePathAt(uint monitorIndex);

            [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            uint GetMonitorDevicePathCount();

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            RECT GetMonitorRECT([MarshalAs(UnmanagedType.LPWStr)] string monitorID);

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            void SetBackgroundColor(uint color);

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            uint GetBackgroundColor();

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            void SetPosition([MarshalAs(UnmanagedType.I4)] DESKTOP_WALLPAPER_POSITION position);

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            [return: MarshalAs(UnmanagedType.I4)]
            DESKTOP_WALLPAPER_POSITION GetPosition();

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            //void SetSlideshow(IShellItemArray items);
            void SetSlideshow(IntPtr items);

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            //IShellItemArray GetSlideshow();
            IntPtr GetSlideshow();

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            void SetSlideshowOptions(uint options, uint slideshowTick);

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            void GetSlideshowOptions(out uint options, out uint slideshowTick);

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            void AdvanceSlideshow([MarshalAs(UnmanagedType.LPWStr)] string monitorID, [MarshalAs(UnmanagedType.I4)] DESKTOP_SLIDESHOW_DIRECTION direction);

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            DESKTOP_SLIDESHOW_STATE GetStatus();

            //[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
            void Enable([MarshalAs(UnmanagedType.Bool)] bool enable);
        }
        // The wall paper interface.
        private IDesktopWallpaper wallpaper;
        // Constructor.
        public WallpaperDetails()
        {
            var clsid = new Guid("C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD");
            var type = Type.GetTypeFromCLSID(clsid);
            wallpaper = (IDesktopWallpaper)Activator.CreateInstance(type);
        }
        // Set the wallpaper for all monitors to the specified image path. Returns 0 on success, -1 on failure.
        public Int32 SetWallpaper(String pathToWallpaper)
        {
            try
            {
                String fullPathToWallpaper = Path.GetFullPath(pathToWallpaper);
                if (!File.Exists(fullPathToWallpaper))
                {
                    Console.WriteLine($"Error: File does not exist at path {fullPathToWallpaper}");
                    return -2; // Failure
                }
                // NULL => all monitors, we set the wallpaper for all monitors at once instead of looping through each monitor.
                wallpaper.SetWallpaper(null, fullPathToWallpaper);
                /*
                // Logic for iterating over the monitors.
                uint mCount = wallpaper.GetMonitorDevicePathCount();
                for (uint i = 0; i < mCount; i++)
                {
                    // Set the wallpaper.
                    wallpaper.SetPosition(DESKTOP_WALLPAPER_POSITION.DWPOS_FILL); // Set the wallpaper position to fill for all monitors.
                    wallpaper.SetWallpaper(wallpaper.GetMonitorDevicePathAt(i).ToString(), fullPathToWallpaper);
                }
                */
                return 0; // Success
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error setting wallpaper: {ex.Message}");
            }
            return -1; // Failure
        }
        // Print some details like the number of monitors, their IDs, the wallpaper path for each monitor, and the wallpaper position.
        public void GetWallpaperDetails()
        {
            try
            {
                uint count = wallpaper.GetMonitorDevicePathCount();
                Console.WriteLine($"Number of monitors: {count}");
                for (uint i = 0; i < count; i++)
                {
                    string monitorID = wallpaper.GetMonitorDevicePathAt(i).ToString();
                    string wallpaperPath = wallpaper.GetWallpaper(monitorID).ToString();
                    Console.WriteLine($"Monitor {i + 1}: ID = {monitorID}\nWallpaper = {wallpaperPath}");
                    RECT monitorRect = wallpaper.GetMonitorRECT(monitorID);
                    Console.WriteLine($"Monitor {i + 1} RECT: ({monitorRect.Left}, {monitorRect.Top}, {monitorRect.Right}, {monitorRect.Bottom})");
                }
                Console.WriteLine($"Wallpaper Position: {wallpaper.GetPosition()}");
                string bgColor = wallpaper.GetBackgroundColor().ToString("X6"); // Get the background color in hexadecimal format.
                Console.WriteLine($"Wallpaper Background Color: #{bgColor}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }
    }
}