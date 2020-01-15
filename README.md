# vm-automation
Python script that can be used to automate testing of software/scripts/etc on VMs (currently only VirtualBox is supported). Based on VBoxManage command line interface and does not require VirtualBox SDK.

Both Windows and Linux are supported as host OS.

# Downloads
Stable versions are available in [Releases](https://github.com/Pernat1y/vm-automation/releases)

# Configuration / usage:
Essential commands:
```
python demo.py putty.exe --vms w10_x64 w10_x86 --snapshots dotnet3 dotnet4
```

All options:
```
python demo.py \
    putty.exe \ 
    --vms w10_x64 w10_x86 \
    --snapshots dotnet3 dotnet4 \
    --vboxmanage /usr/bin/vboxmanage \
    --timeout 60 \
    --info 1 \
    --threads 2 \
    --ui gui \
    --login user \
    --password 12345678 \
    --remote_folder desktop \
    --network keep \
    --resolution '1920 1080 32' \
    --pre 'C:\start.cmd' \
    --post 'C:\stop.cmd'
```

# TODO:
* Implement better web interface
* VMware Workstation Pro support (maybe)

# Changelog
Version 0.6.1:
* All functions now return exactly 3 values: [exit_code, stdout, stderr]
* New function to get IP addresses of guest - vm_functions.list_ips(vm)
* Fixes in arguments parser

Version 0.6:
* Script now can use all available VMs ('--vms all') and snapshots ('--snapshots all'). Use with caution and make sure you have only testing VMs
* New function to get list of snapshots for specific VM - vm_functions.list_snapshots(vm)
* Script updated to handle keyboard interrupts (Ctrl+C)
* Option to set random screen resolution from most common ones ('--resolution random')
* Some tweaks and fixes

Version 0.5:
* All functions moved to external files: vm_functions (all VM control functions) and support_functions (randomize filename, calculate hash and show links to Google/VT)
* Main routine moved to file demo.py
* New function to get list of VMs - vm_functions.list_vms()
* Fixed logic when file was removed before execution - script will move on to the next task without waiting for timeout

Version 0.4:
* Updated to use 'argparse' to parse command-line arguments
* All of the settings now can be configured via the command line (see '--help' or examples above)

Version 0.3.1-0.3.2:
* Optionally calculate sha256 hash of a file and show links to VirusTotal and Google searches
* Small fixes

Version 0.3:
* Added option to enable/disable network for guest OS
* Added option to start scripts before/after running the main file
* Added option to change the display resolution
* Code refactoring

Version 0.2:
* Added parallel execution of multiple VMs
* Code refactoring

Version 0.1:
* First public release

# Example videos
* Windows host (version 0.5):

<a href="http://www.youtube.com/watch?feature=player_embedded&v=esA5Mltsfy0" target="_blank"><img src="http://img.youtube.com/vi/esA5Mltsfy0/0.jpg" width="320" height="240" border="10" /></a>

* Linux host (version 0.2-0.3):

<a href="http://www.youtube.com/watch?feature=player_embedded&v=pao3KihklV4" target="_blank"><img src="http://img.youtube.com/vi/pao3KihklV4/0.jpg" width="320" height="240" border="10" /></a>

# Donations
You can support further development with a donation (Thanks!)

BTC: bc1q2ywqf2pc7mak2xf24f56n9y5s6mg3rgec53y86helw8n8mcyrn0sagcfr7

