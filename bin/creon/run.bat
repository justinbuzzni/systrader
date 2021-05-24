call C:\Users\%username%\Anaconda3x86\Scripts\activate.bat
python C:\Users\%username%\systrader\bin\creon\kill.py
python C:\Users\%username%\systrader\quantylab\systrader\creon\_creon.py disconnect
python C:\Users\%username%\systrader\quantylab\systrader\creon\_creon.py connect --id=%1 --pwd=%2 --pwdcert=%3
python C:\Users\%username%\systrader\manage.py runserver 0.0.0.0:8000 --noreload