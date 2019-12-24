# vm-automation
Python script that can be used to automate testing of software/scripts/etc on VMs (currently only VirtualBox is supported).

Both Windows and Linux are supported as host OS.

# Configuration / usage:
As version 0.4 all options are set via command line arguments:

Essential commands example:
```
python demo.py putty.exe --vms w10_1903_x64 w10_1903_x86 --snapshots live
```

Extended example:
```
python demo.py \
    putty.exe \ 
    --vms w10_1903_x64 w10_1903_x86 \
    --snapshots live \
    --vboxmanage vboxmanage \
    --timeout 60 \
    --hash 1 \
    --links 1 \
    --ui gui \
    --login user \
    --password 12345678 \
    --remote_folder Desktop \
    --network keep \
    --resolution '1920 1080 24' \
    --pre 'C:\Procmon\Procmon.exe /AcceptEula /Minimized /Quiet /BackingFile Procmon.pml' \
    --post 'C:\Procmon\Procmon.exe /Terminate'
```

# TODO:
* Control how many threads run simultaneously (currently equals to the number of VMs)
* ? Implement web interface
* ? VMware Workstation Pro support

# Changelog
Version 0.5:
* All functions moved to external file
* New functions to get information about VMs
* Fixed logic when file was removed before execution

Version 0.4:
* Updated to use 'argparse' to parse command-line arguments
* All of the settings now can be configured via the command line (see '--help' or examples above)

Version 0.3.1-0.3.2:
* Optionally calculate sha256 hash of a file and show links to VirusTotal and Google searches
* Fix some warnings
* Small fixes

Version 0.3:
* Added option to enable/disable network for guest OS
* Added option to start scripts before/after running the main file
* Added option to change the display resolution
* Code refactoring

Version 0.2:
* Added multithreading
* Code refactoring

Version 0.1:
* First public release

# Example videos
* Windows host (version 0.2):

<a href="http://www.youtube.com/watch?feature=player_embedded&v=nIj4cW_miuA" target="_blank"><img src="http://img.youtube.com/vi/nIj4cW_miuA/0.jpg" width="320" height="240" border="10" /></a>

# Donations
You can support further development with a donation (Thanks!)

BTC: bc1q2ywqf2pc7mak2xf24f56n9y5s6mg3rgec53y86helw8n8mcyrn0sagcfr7


