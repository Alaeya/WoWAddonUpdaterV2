# WoWAddonUpdaterV2
lightweight Updater for WoW-Addons

0) You need Python 3.6 (programming language like C#, Java, etc.) to run this programm.
   Download and install Python here:
   https://www.python.org/downloads/release/python-366/

1) Edit the 'config.ini'-file:
     WoW Addon Location = D:\Games\World of Warcraft\Interface\Addons
         Path to your World of Warcraft\Interface\Addons folder
         
     Addon List File = AddonList.txt
         Filename of your Addons you want to install & update (usually no need to edit this)
         
     Installed Versions File = installedVersions.txt
         Filename of the file where the WoWAddonUpdaterV2 will store the currently installed Addonversions (usually no need to edit this; if so rename the file which comes with this repository)
     
     Close Automatically When Completed = False
         Whether the commandshell will close after finishing (=True) or will stay open until the user presses 'ENTER' (=False))
         
2) Edit and fill the AddonList.txt-file with links to the Addonpage (currently curse and elvui only)
   An entry should look like this:
   https://www.curseforge.com/wow/addons/acp
   
3) Run 'Run WoWAddonUpdaterV2.bat' to update/install Addons

(To delete Addons you need to delete the corresponding entry in the AddonList.txt-file and delete the folder in your Interface\Addons directory)
