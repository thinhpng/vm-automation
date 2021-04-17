@echo off

@echo Building Windows binary...

cd ..
del /S /Q demo_cli.dist
python -m nuitka --standalone --remove-output demo_cli.py
move demo_cli.dist\demo_cli.exe vm_automation_windows.exe
upx.exe -q -9 vm_automation_windows.exe
pause
