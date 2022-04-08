@echo off
pip install -r requirements.txt
cls
echo Installed Dependencies

set /p question="Enable Auto Start (Y/N)? "
if "%question%"=="Y" (
    echo Enabling Auto Start
    powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('"%userprofile%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\SelfBot.lnk"');$s.TargetPath='%~dp0\start.bat';$s.WorkingDirectory='%~dp0';$s.WindowStyle=7;$s.Save()"
)
pause