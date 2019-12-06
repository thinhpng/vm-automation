# vm-automation
Python script that can be used to automate testing of software/scripts/etc on VMs (currently only VirtualBox is supported).

Both Windows and Linux are supported as host OS.

# Configuration
As version 0.4 all options are set via command line arguments:
```
python vm-automation.py --help                                                                                                    usage: vm-automation [-h] --vms [VMS [VMS ...]] --snapshots [SNAPSHOTS [SNAPSHOTS ...]] [--vboxmanage [VBOXMANAGE]] [--timeout [TIMEOUT]] [--hash [{1,0}]] [--links [{1,0}]]
                     [--ui [{gui,headless}]] [--login [LOGIN]] [--password [PASSWORD]] [--destination [DESTINATION]] [--network [{on,off,keep}]] [--resolution [RESOLUTION]] [--pre [PRE]]
                     [--post [POST]]
                     file [file ...]

optional arguments:
  -h, --help            show this help message and exit

Required options:
  file                  Path to file
  --vms [VMS [VMS ...]]
                        Space-separated list of virtual machines to use
  --snapshots [SNAPSHOTS [SNAPSHOTS ...]]
                        Space-separated list of snapshots to use

Main options:
  --vboxmanage [VBOXMANAGE]
                        Path to vboxmanage binary (default: vboxmanage)
  --timeout [TIMEOUT]   Timeout in seconds for both commands and VM (default: 60)
  --hash [{1,0}]        Calculate and print hash for file (default: 1)
  --links [{1,0}]       Show links to VirusTotal and Google search (default: 1)

Guests options:
  --ui [{gui,headless}]
                        Start VMs in GUI or headless mode (default: gui)
  --login [LOGIN]       Login for guest OS (default: user)
  --password [PASSWORD]
                        Password for guest OS (default: P@ssw0rd)
  --destination [DESTINATION]
                        Destination folder in guest OS to place file (default: C:\Users\%vm_login%\Desktop\)
  --network [{on,off,keep}]
                        State of guest OS network (default: keep)
  --resolution [RESOLUTION]
                        Screen resolution for guest OS (default: 1024 768 32)
  --pre [PRE]           Script to run before main file (default: False)
  --post [POST]         Script to run after main file (default: False)
```

Example:
```
python vm-automation.py putty.exe --vms w10_1903_x64 w10_1903_x86 --snapshots live
```

# Usage
python vm-automation.py binary.exe

# TODO:
* Control how many threads run simultaneously (currently equals to the number of VMs)
* Implement some sort of the web interface (Django?)

# Changelog
Version 0.4:
* All of the settings now can be configured via the command line (see '--help')
* Updated to use 'argparse' to parse command-line arguments

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

