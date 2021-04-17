@echo off
@echo This file is just to test general functionality in live mode on Windows host. Open in notepad to see all options.
pause
python ../demo_cli.py --vms ws2019 --snapshots live --timeout 60 --delay 5 --threads 1 --verbosity debug --report --record --pcap --memdump --ui gui --login administrator --password "12345678" --remote_folder desktop --open_with "%windir%\\explorer.exe" --network on ../putty.exe
pause

