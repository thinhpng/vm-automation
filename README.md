# vm-automation
Python script that can be used to automate testing of software/scripts/etc on VMs (currently only VirtualBox is supported). Based on VBoxManage command-line interface and does not require VirtualBox SDK.

Both Windows and Linux are supported as host OS.

# Downloads
Stable versions are available in [Releases](https://github.com/Pernat1y/vm-automation/releases)

# Usage:
Essential commands (command-line interface):
```
python demo_cli.py \
    putty.exe \
    --vms windows10 windows8 windows7 \
    --snapshots firefox chrome edge
```

All options (command-line interface):
```
python demo_cli.py \
    putty.exe \ 
    --vms windows10 windows8 windows7 \
    --snapshots firefox chrome ie \
    --vboxmanage /usr/bin/vboxmanage \
    --timeout 60 \
    --info 1 \
    --threads 2 \
    --verbosity info \
    --log vm_automation.log \
    --ui gui \
    --login user \
    --password 12345678 \
    --remote_folder desktop \
    --uac_fix 1 \
    --uac_parent 'C:\\Windows\\Explorer.exe' \
    --network keep \
    --resolution '1920 1080 32' \
    --pre 'C:\start.cmd' \
    --post 'C:\stop.cmd'
```

# Host configuration
* Both Windows and Linux are tested as host OS. May work on other platforms, supported by VirtualBox.
* You need VirtualBox (the newer the better). Proprietary Oracle VM VirtualBox Extension Pack is *not* required.
* It is recommended to have folder with 'vboxmanage' binary in the environment variables.
* You need a recent version of Python (3.7+).

# Guest configuration
* You must have Windows as the guest OS with autologin configured (or have a snapshot with a user logged in).
* You must have VirtualBox guest additions installed.
* It is strongly recommended to have live snapshots to restore to (otherwise it will be *much* slower).
* Guest disk encryption is *not* supported (at least for now. VBoxManage limitation).
* Files, that require UAC elevation, are *not* supported (at least for now. VBoxManage limitation).

# TODO:
* Distribute workload to multiple physical hosts.
* Implement web interface.
* Add option to use pre-running VMs.
* Add global progress status.
* Vagrant integration (maybe).
* Code optimization and fixes.
* Better tests coverage.

# Changelog
Version 0.8.1:
* Fixed bug with some command line args were ignored (--ui).

Version 0.8:
* Added options 'uac_fix' and 'uac_parent' for vm_exec() function.
Used to circumvent VirtualBox error VERR_PROC_ELEVATION_REQUIRED, when trying to execute application with mandatory UAC elevation.
* Added short aliases for '--vms' and '--snapshots' options: '-v' and '-s'.
* Added option 'dictionary' for list_vms() function. List of VMs will be returned as {'vm': '/group'} dictionary.
* Added function to clone VM - vm_clone().
* Added function to record guest screen - vm_record().
* Added option to restore current snapshot: vm_snapshot_restore('vm', 'restorecurrent').
* Updated vm_screenshot() function - code to generate image index moved to main script.
* All files converted to Unix EOL (LF).

Version 0.7.3:
* Docstring added for all the functions (Sphinx format). Usage: help(function_name).
* Added functions to export and import VMs - vm_export() and vm_import(). Have separate timeout settings as operations are time consuming.

Version 0.7.2:
* Added function to enumerate guest properties - vm_enumerate().
* Updated list_ips() function.
* Added functions to control snapshots - vm_snapshot_take() and vm_snapshot_remove(). Currently not used.

Version 0.7.1:
* Added option to redirect log to file ('--log vm_automation.log'). Default: log to console ('--log console').

Version 0.7:
* Added option to control number of concurrently running tasks ('--threads 2'). Set to '0' to set to number of VMs.
* Added option to control log verbosity ('--verbosity debug|info|error').
* Added parameter ignore_status_error to vm_stop() function. Can be used when trying to stop already stopped VM. Disabled by default.
* Added aliases for vm_copyto() and vm_copyfrom() functions - vm_upload() and vm_download().
* Fixed command line arguments processing.
* Added unittests for some of the functions ('tests/test.py').
* Other minor updates for few functions.

Version 0.6.2:
* Bug fixes in list_snapshots() function.

Version 0.6.1:
* All vm_functions are now returning exactly 3 values: [exit_code, stdout, stderr].
* New function to get IP addresses of guest - vm_functions.list_ips(vm).
* Fixes in arguments parser.

Version 0.6:
* Script now can use all available VMs ('--vms all') and snapshots ('--snapshots all'). Use with caution and make sure you have only testing VMs.
* New function to get list of snapshots for specific VM - vm_functions.list_snapshots().
* Script updated to handle keyboard interrupts (Ctrl+C).
* Option to set random screen resolution from most common ones ('--resolution random').
* Some tweaks and fixes.

Version 0.5:
* All functions moved to external files: vm_functions (all VM control functions) and support_functions (randomize filename, calculate a hash and show links to Google/VT).
* The main routine moved to file demo.py.
* New function to get list of VMs - vm_functions.list_vms().
* Fixed logic when the file was removed before execution - script will move on to the next task without waiting for a timeout.

Version 0.4:
* Updated to use 'argparse' to parse command-line arguments.
* All of the settings now can be configured via the command line (see '--help' or examples above).

Version 0.3.1-0.3.2:
* Optionally calculate sha256 hash of a file and show links to VirusTotal and Google searches.
* Small fixes.

Version 0.3:
* Added option to enable/disable network for guest OS.
* Added option to start scripts before/after running the main file.
* Added option to change the display resolution.
* Code refactoring.

Version 0.2:
* Added parallel execution of multiple VMs.
* Code refactoring.

Version 0.1:
* First public release.

# Example videos
* Windows host (version 0.7.2):

<a href="http://www.youtube.com/watch?feature=player_embedded&v=t6AWew06rxo" target="_blank"><img src="http://img.youtube.com/vi/t6AWew06rxo/0.jpg" width="320" height="240" border="10" /></a>

* Linux host (version 0.7.3):

<a href="http://www.youtube.com/watch?feature=player_embedded&v=QnXfmPVbmlo" target="_blank"><img src="http://img.youtube.com/vi/QnXfmPVbmlo/0.jpg" width="320" height="240" border="10" /></a>

# Donations
You can support further development with a donation (Thanks!).

<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XQABQMPTCN388&source=url" target="_blank"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif"></img></a>

BTC: bc1qstm95hfx26sf89h62xt804cfzg48z5qxe6cff63ff3s5d2f8f8nq3jf3u4

