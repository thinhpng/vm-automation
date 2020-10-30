@echo off
@echo Building Windows binary...
cd ..
call "C:\Program Files\Python38\Scripts\nuitka.bat" --standalone --remove-output demo_cli_no_version_check.py
move demo_cli_no_version_check.dist\demo_cli_no_version_check.exe vm_automation_windows.exe
upx.exe -q -9 vm_automation_windows.exe
