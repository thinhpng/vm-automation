@echo off
@echo This file is just to test general functionality in live mode on Windows host. Open in notepad to see all options.
pause

rem rmdir /s /q reports

rem python ../demo_cli.py --vms ws2019 --snapshots live --duration 60 --delay 5 --threads 1 --verbosity debug --report --record --pcap --memdump --ui gui --login administrator --password "12345678" --remote_folder desktop --open_with "%windir%\\explorer.exe" --network on ./1.exe

python ../demo_cli.py --vms w10 --snapshots ESET Avira Bitdefender Avast Malwarebytes Kaspersky DrWeb Comodo Sophos --duration 40 --delay 5 --threads 1 --verbosity info --report --record --pcap --ui 0 --login admin --password "12345678" --remote_folder desktop --open_with "%windir%\\explorer.exe" --network on ./1.exe

pause

