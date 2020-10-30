#!/usr/bin/bash

cd ..

if command -v nuitka>/dev/null; then
    nuitka --standalone --remove-output demo_cli_no_version_check.py
    mv demo_cli_no_version_check.dist\demo_cli_no_version_check.exe vm_automation_windows.exe
else
    echo 'Nuitka not found. Exiting.'
    exit 1
fi

if command -v upx>/dev/null; then
    echo 'Compressing binary with UPX.'
    upx -q -9 vm_automation_windows.exe
else
    echo 'UPX no found. Skipping.'
fi
