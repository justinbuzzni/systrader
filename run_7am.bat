rem You need to copy, modify example_activate.bat as activate.bat for this script

echo "Server script"
call activate.bat
python wait7am.py
python kiwoom_restful.py
pause
