# Folder to download the pictures to.
$downloadFolder = "$env:USERPROFILE\Pictures\Wallpapers"
# Create the folder if it is not already present.
if( -not (Test-Path -Path $downloadFolder)) {
  New-Item -Path $downloadFolder -ItemType Directory -ErrorAction SilentlyContinue
}
# Global var to hold downloaded image file name
$Global:wallpaperFile = $null

# A rudimentary method to get the filename from the URL.
# This is based on my observation of the image URL only.
# Will have to rewrite if the URL structure changes.
function Get-FilenameFromURL {
  param (
    [string]$url = "__UNKNOWN__"
  )
  try {
    if($url -eq "__UNKNOWN__") { return $null }
    $fname = $url
    $fname = $fname.Replace("_ds_", "_") # Get rid of the _ds_ if it is present.
    $fname = $fname.Substring($fname.IndexOf("_")+1)
    $fname = $fname.Substring($fname.IndexOf("_")+1)
    $fname = $fname.Substring(0,$fname.IndexOf("_"))
    return $fname
  } catch {
    "Error extracting filename from $url : $_"
    return "Spotlight"
  }
}

function Download-SpotlightWallpaper {
    param (
        [string]$url = "https://fd.api.iris.microsoft.com/v4/api/selection?&placement=88000820&bcnt=1&country=IN&locale=en-IN&fmt=json"
    )
    
    try {
        $Global:wallpaperFile = $null
        $request = Invoke-WebRequest -Uri $url -UseBasicParsing
        $json = $request.Content | ConvertFrom-Json
        
        # The response has nested JSON in the item field
        $itemJson = $json.batchrsp.items[0].item | ConvertFrom-Json
        # Extract the image download URL
        $imageUrl = $itemJson.ad.landscapeImage.asset
        
        if ($imageUrl) {
            $fname = Get-FilenameFromURL($imageUrl)
            if(-not $fname) { throw "Unable to extract filename from $imageUrl" }
            # Generate a filename, e.g., using current date
            [string]$date = Get-Date -Format "yyyyMMdd-hhmmss.fff"
            [string]$wpfile = "$downloadFolder\$fname" + "_$date.jpg"
            
            "Downloading Spotlight wallpaper from $imageUrl as $wpfile"
            Invoke-WebRequest -Uri $imageUrl -OutFile $wpfile -ErrorAction SilentlyContinue
            if (Test-Path -Path $wpfile) {
                $Global:wallpaperFile = $wpfile
            }
        } else {
            "No landscapeImage found in the response."
        }
    } catch {
        "Error downloading Spotlight wallpaper: $_"
    }
}
# Set the wallpaper to the file specified.
# If no file is specified, we will use the global variable for the name.
function Set-WallpaperFromFile {
  param (
    [string]$wfile = $Global:wallpaperFile
  )
  try {
    if(([string]::IsNullOrEmpty($wfile))) { throw "No wallpaper file specified." }
    [string]$exeName = "D:\Tools\DownloadNSetWallpaper\SetWallpaper.exe"
    $myProcess = Start-Process -Wait -PassThru -FilePath $exeName -ArgumentList $wfile
    if($myProcess.ExitCode -ne 0) { throw "SetWallpaper.exe returned non-zero code: " + $myProcess.ExitCode }
    # Exe completed with success. Update the registry for good measure.
    Set-ItemProperty -Path "HKCU:Software\Microsoft\Windows\CurrentVersion\Explorer\Wallpapers" -Name CurrentWallpaperPath -Value $wfile
  } catch {
    "Exception while setting wallpaper: $_"
  }
}
# Main function
Download-SpotlightWallpaper
Set-WallpaperFromFile