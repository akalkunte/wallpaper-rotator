using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Principal;
using System.Text;
using System.Threading.Tasks;

namespace WindowsWallpaper
{
    internal class Program
    {
        static int Main(string[] args)
        {
            try
            {
                WallpaperDetails wp = new WallpaperDetails();
                if (args.Length == 0)
                {
                    wp.GetWallpaperDetails();
                    Console.WriteLine("\nNo arguments provided. Please provide the path to the image to set as wallpaper.");
                    Console.WriteLine("The program will attempt to set the provided image as wallpaper on all monitors in FILL screen mode.\n");
                    return -1; // Did not do anything.
                }
                // Take the first argument as the path to the image to set as wallpaper.
                wp.SetWallpaper(args[0]);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred: {ex.Message}");
                return -2; // Error.
            }
            return 0; // Success
        }
    }
}
