# 개발 환경

- Anaconda Python 3.5+ x86

# Setup

## 키움증권 환경 설치

- Kiwoom Open API 설치
- MS Visual C++ 2010 x86 설치 (mfc100.dll 에러 해결)
- MS Visual C++ 2012 x86 설치
- KOA Studio 실행

## 크레온 환경 설치

```
conda install -c anaconda python=3.8.2
conda install -c anaconda pywin32
pip install django
pip install pywinauto
```

pywinauto가 3.7.6, 3.8.1 등의 버전에서는 동작하지 않으므로 3.7.4, 3.8.0, 3.8.2 등 사용

# 문서

## 키움증권
- [파이썬을 이용한 자동 주식투자 시스템 개발 튜토리얼 - 키움증권편](http://blog.quantylab.com/systrading.html)
- http://blog.quantylab.com/systrading.html

## 대신증권 크레온
- [대신증권 크레온(Creon) API를 사용하여 파이썬에서 주식 차트 데이터 받아오기](http://blog.quantylab.com/creon_chart.html)
- [대신증권 크레온(Creon) HTS 브리지 서버 만들기 (Flask 편)](http://blog.quantylab.com/creon_hts_bridge.html)
- [대신증권 크레온(Creon) HTS 브리지 서버 만들기 (Django 편)](http://blog.quantylab.com/creon_hts_bridge_django.html)
- [대신증권 크레온 API로 실시간 주가 데이터 받기](http://blog.quantylab.com/2021-04-23-creon_realtime.html)

# Windows Scheduler

- 리부팅: `C:\Windows\System32\shutdown.exe /r`