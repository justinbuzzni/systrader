call C:\Users\quantylab\Anaconda3x86\Scripts\activate.bat
python C:\Users\quantylab\systrader\bin\creon\kill.py
python C:\Users\quantylab\systrader\quantylab\systrader\creon\_creon.py disconnect
python C:\Users\quantylab\systrader\quantylab\systrader\creon\_creon.py connect --id=%1 --pwd=%2 --pwdcert=%3
python C:\Users\quantylab\systrader\manage.py runserver 0.0.0.0:8000 --noreload