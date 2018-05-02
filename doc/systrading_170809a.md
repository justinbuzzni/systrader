파이썬을 이용한 자동 주식투자 시스템 개발 튜토리얼 - 키움증권편

# 들어가는 글

많은 분들이 주식투자를 해보셨거나 적어도 관심은 있으실 것입니다. 그러나 막상 주식투자를 해서 수익을 내는 분들은 많지 않은 것이 현실입니다. 많은 분들이 주식시장에서 이기지 못합니다. 그 이유는 욕심때문에 종목 매매를 객관적으로 하지 못해서, 계속해서 주식시장을 들여다볼 시간이 없어서일 수 있습니다. 시스템 트레이딩은 정해진 규칙으로 객관적으로 종목을 매매하여 객관성을 유지하고, 시스템이 자동으로 투자하기 때문에 주식시장을 계속 들여다보지 않아도 되는 등의 다양한 장점을 가집니다. 이 책을 통해 자신만의 자동 투자 시스템을 구현하여 모두 주식시장에서 성공적인 투자자가 될 수 있기를 바라봅니다.

이 책은 핵심만을 다루고, 진행하다 막히는 부분이 있으면 카페를 통해 트러블슈팅 (Trouble Shooting)을 도와드립니다.

> 카페: http://cafe.naver.com/pysystrader

# 환경 설치

파이썬에서 키움증권 API를 사용하여 자동투자 시스템을 개발하는데 다음 환경을 권장합니다.
- 윈도우 7+
- 파이썬 3.5+ x86(32 비트)
- PyCharm
- 키움증권 API

## 파이썬 환경 설치

여기서는 파이썬 3.5+ 32비트 버전을 사용합니다. 파이썬 2를 사용해도 무방하지만 32비트를 사용해야 합니다. 그리고 꼭 파이썬 2를 사용해야 하는 것이 아니라면 파이썬 3를 사용할 것을 권장합니다.

추가로 파이썬 라이브러리들을 설치해야 하는데, 본 튜토리얼에서 사용하는 주요 라이브러리들은 다음과 같습니다.

- PyQt5
- NumPy
- Pandas

Anaconda3는 파이썬 3와 대부분의 주요 라이브러리들을 포함하고 있습니다. 번거로움을 줄이고자 이들을 별도로 설치하는 것 보다 Anaconda3를 설치하기를 권장합니다.

### Anaconda3 설치

다음 사이트에서 무료로 Anaconda3를 받을 수 있습니다. 

`https://www.continuum.io/downloads`

![](img\anaconda3.png)
Anaconda3 다운로드 사이트 화면. 왼쪽 아래의 빨간 박스로 표시한 링크를 다운받기를 권장합니다.

다운받은 파일로 설치를 진행합니다. 별도의 설정 변경 없이 설치를 진행하면 되기 때문에 어려운 부분은 없습니다.

### PyCharm 설치

다음 사이트에서 무료로 PyCharm Community 버전을 다운받을 수 있습니다.

`https://www.jetbrains.com/pycharm/`

Professional 버전은 유료이니 Community 버전을 받으시면 됩니다. Community 버전도 자동 투자 시스템을 만드는데 충분합니다.

## 키움증권 API 설치

이제 키움증권의 Open API를 설치할 차례입니다. 먼저 브라우저를 통해 키움증권 홈페이지([https://www1.kiwoom.com](https://www1.kiwoom.com))에 들어갑니다. 메인화면의 최하단을 보시면 다음과 같이 `Open API` 메뉴가 있습니다.

![](img\openapi1.png)

클릭하여 들어가시면 다음과 같은 화면을 볼 수 있습니다.

![](img\openapi2.png)

여기서 표시해 놓은 `사용 신청하러 가기`와 `키움 Open API+ 모듈 다운로드`를 진행해 주시면 됩니다.

이렇게 다운받은 `OpenAPISetup.exe`파일을 실행시켜서 설치하시면 키움증권 API 설치가 완료됩니다.

추가로 `KOA Studio`를 설치하여 키움증권 API를 살펴볼 수 있습니다. `KOA Studio`를 실행했을 때 `mfc100.dll`을 찾을 수 없다는 에러화면을 보게 될 수도 있습니다.

![](img\koastudio에러.png)

이 때는 `MS Visual C++ 2010 x86`을 설치하면 에러가 해결됩니다.

> MS VC++ 다운로드 페이지: https://www.microsoft.com/en-us/download/details.aspx?id=5555

# 모의투자 준비

## 키움증권 계좌 개설

키움증권을 통해 주식 투자를 하기 위해 우선 키움증권 계좌를 개설해야 합니다. 키움증권 홈페이지 메인화면의 우측에 다음 화면이 있습니다.

![](img\계좌개설.png)

여기서 `키움 계좌 개설` 메뉴를 클릭하시고 계좌 개설을 진행해 주시면 됩니다.

## 모의투자 신청

자동투자 시스템을 구현하면서는 모의투자 계좌를 이용하셔야 합니다. 키움증권 홈페이지 메인화면의 최하단을 보시면 다음과 같이 `상시 모의투자` 메뉴가 있습니다.

![](img\모의투자1.png)

클릭하여 들어가시면 왼쪽 메뉴 리스트에 `참가신청` 메뉴가 있고, 클릭하여 들어가시면 다음과 같이 상시모의투자 참가신청란이 있습니다.

![](img\모의투자2.png)

신청 완료하시면 왼쪽 메뉴 리스트의 `계좌정보` 메뉴를 통해 주식계좌를 확인할 수 있습니다.

# 키움증권 API 살펴보기

키움증권 API는 크게 TR과 REAL로 구분되는 API 집합으로 구성되어 있습니다.

- TR은 요청을 보내면 그 결과가 콜백 함수로 전달되는 API들로, 시세조회, 관심종목조회, 조건검색 등을 포함합니다.
- REAL은 키움증권 시스템에서 콜백 함수에 실시간으로 데이터를 전달하는 API들로, 매매 체결, 업종/종목의 실시간 시세, 실시간 조검검색 등을 포함합니다.

`KOA Studio`프로그램을 이용하면 API에 대한 상세 정보를 확인할 수 있습니다. 

앞으로 활용할 주요 API들을 살펴보겠습니다. 여기서는 API에 포함되어 있는 함수들의 형태 (Signature)만 보여주고 파이썬에서의 호출 방법은 뒤에서 설명합니다.

## 로그인

로그인 함수는 아주 간단합니다. `CommConnect()`를 호출하면 키움증권 로그인 창이 뜨고 로그인 성공시 `1`, 로그인 실패시 `0`을 반환합니다. 키움증권 로그인 창이 뜨면 아이디, 비밀번호, 공인인증서비밀번호 입력란이 있습니다. 개발 동안에는 모의투자를 체크하여 아이디와 비밀번호만 입력하시길 강력 권장합니다.

키움증권의 로그인 창은 다음과 같습니다. 여기서 아이디를 저장하고, 모의투자 모드로 설정할 수 있습니다. 이 창을 파이썬으로 띄우는 방법은 개발 관련 장에서 설명합니다.

![](img\로그인1.png)

그렇다면 매번 아이디, 비밀번호, 공인인증서번호를 입력해야 할까요? 다행히 자동로그인 기능이 있습니다. 먼저 계좌 비밀번호를 저장해야 합니다. 이를위해 다음과 같이 Windows 우측 하단의 트레이 아이콘을 우클릭하여 `계좌비밀번호 저장` 메뉴를 통해 계좌 비밀번호를 저장할 수 있습니다. 트레이 아이콘이 숨어져 있을 수도 있으니, 화살표를 눌러서 확인해보시기 바랍니다. 물론 로그인이 되어 있는 상태에서만 아이콘을 확인할 수 있으니, 개발 관련 장에서 확인하시면 됩니다.

![](img\계좌비밀번호저장1.png)

다음과 같이 자동로그인을 활성화할 수 있습니다. 먼저 계좌 비밀번호를 등록하고, 계좌번호 바로 밑에 있는 `AUTO`를 체크합니다. 이렇게 하면 앞으로 로그인할 때 비밀번호를 입력하지 않아도 자동으로 로그인이 됩니다.

![](img\계좌비밀번호저장2.png)

## 계좌

### 주문 가능 금액 확인

이제 키움증권 API를 사용할 환경이 갖추어 졌습니다. 로그인한 계좌의 현황을 확인할 수 있는 API들을 살펴보겠습니다. 살펴볼 주요 API는 다음과 같습니다.

- 현재 잔고 (Balance) 확인
- 보유 종목 확인

현재 잔고를 확인하는 API는 `예수금상세현황요청` 기능을 이용하시면 됩니다. `TR 목록`의 `opw00001`을 활용하면 됩니다. 호출 방법은 다음과 같습니다.

```python
SetInputValue("계좌번호", <계좌번호>)
CommRqData("예수금상세현황요청", "opw00001", 0, <화면번호>)
```

여기서 `<계좌번호>`에는 여러분의 모의투자 계좌번호를 입력하시면되고, `화면번호`에는 임의의 값을 정해주시면 됩니다. 이렇게 호출하면 `OnReceiveTrData()` 함수가 콜백됩니다. 콜백이란 필요한 처리 후 시스템에서 함수를 호출해 준다는 의미를 가지는 컴퓨터 용어입니다. 주로 이름이 `On`으로 시작하는 함수들이 콜백 합수입니다.

> 화면번호의 값을 상수화하여 사용하시길 권장합니다. 키움증권에서 사용할 수 있는 화면번호가 200개로 제한되어 있기 때문입니다.

`OnReceiveTrData()`의 형태는 다음과 같습니다.

```python
OnReceiveTrData(sScrNo, sRQName, sTRCode, sRecordName, sPreNext, nDataLength, sErrorCode, sMessage, sSPlmMsg)
```

- sScrNo: 화면번호
- sRQName: 사용자 구분명
- sTRCode: TR이름
- sRecordName: 레코드 이름
- sPreNext: 연속조회 유무를 판단하는 값 0: 연속(추가조회)데이터 없음, 2:연속(추가조회) 데이터 있음
- nDataLength: 사용안함
- sErrorCode: 사용안함
- sMessage: 사용안함
- sSPlmMsg: 사용안함

이 콜백 함수 내에서 `sRQName`가 `예수금상세현황요청`인지 확인하고, 다음과 같이 `주문가능금액`을 얻어올 수 있습니다.

```python
GetCommData(sTRCode, sRQName, 0, "주문가능금액")
```

### 보유 종목 수익률 확인

매수 주문을 넣고, 주문이 체결되면 보유 종목이 생깁니다. 보유 종목은 주로 매도의 관점에서 모니터링 해야 합니다. 물론 추가 매수를 할 수도 있습니다. 보유 종목의 수익률을 확인하는 API를 살펴보겠습니다. 보유종목 정보를 받아오는 TR 코드는 `OPT10085` 입니다. 

```python
SetInputValue("계좌번호", <계좌번호>)
CommRqData("계좌수익률요청", "opt10085", 0, <화면번호>)
```

여기서 화면번호를 임의의 문자열을 넣어주면 됩니다. 화면번호는 다른 요청과 겹치지 않는 것이 좋습니다.

## 업종



## 종목


# 자동 투자 시스템 설계

## 모듈 설계

실제로 투자를 할때 하는 일들을 살펴볼 필요가 있습니다. 다음과 같이 정리해 보겠습니다.

- 시장의 상황을 파악합니다. 궂이 불구덩이에 뛰어들 필요는 없습니다. 약세장일때는 피하는게 상책이죠.
- 계좌의 현재 상태를 파악합니다. 매수 가능 금액이 얼마나 있는지 알아야 합니다.
- 매수를 고려할 종목을 선택 합니다. 아무리 강세장에서도 오를 종목만 오릅니다.
- 보유종목을 모니터링 합니다. 자신의 규칙에 따라 익절, 손절하는 것이 필요하죠.
- 매수할 종목을 선택합니다.
- 매도할 보유종목을 선택합니다.
- 투자 손익을 파악합니다.

자동 투자 시스템을 구현할 때, 위 일들을 별도의 모듈로 구현하는 것이 유지보수 측면에서 좋을 것입니다. 위에서 나열한 일들을 수행하는 모듈들을 정해 보겠습니다.

- 시장모니터 (Markets Monitor): 코스피, 코스닥 시장을 모니터링하여 강세장, 약세장을 판단하는 모듈
- 계좌관리자 (Account Manager): 잔고를 파악하는 모듈
- 보유종목모니터 (Holdings Monitor): 보유종목의 수익률 등을 모니터링 하는 모듈
- 종목모니터 (Stocks Monitor): 실시간 종목 검색, 종목 상세 정보 획득 등을 수행하는 모듈
- 매매판단자 (Decision Maker): 종목의 매수, 매도를 판단하는 모듈

## 데이터베이스 스키마 설계

# 자동 투자 시스템 개발

## 파이썬 프로젝트 만들기

파이썬은 컴퓨터 비전공자도 쉽게 접근할 수 있으면서 강력한 고급 프로그래밍 언어입니다. 전세계적으로 사용자가 크게 늘고 있는 추세이고, 구글을 비롯한 여러 업체의 실서비스에서도 사용하고 있습니다. 본 튜토리얼에서는 이후에 나오는 소스코드들을 따라할 수 있을 정도의 문법만 다룹니다.

우선 프로그래밍 언어를 처음 배울 때 꼭 한번씩 해보는 "Hello World!" 문자열을 출력해 보겠습니다.
```python
if __name__ == "__main__":
    print("Hello World!")
```
실행해 보면 `Hello World!`가 출력되는 것을 확인할 수 있습니다.

파이썬으로 객체지향 프로그램을 작성할 수 있습니다. 이를 위해서 파이썬에는 모듈과 클래스 개념이 들어있습니다. 파이썬에서 모듈은 하나의 `.py` 파일이라고 볼 수 있습니다. 하나의 파이썬 파일에 여러 클래스들이 포함될 수 있습니다. 

이제 `main.py` 모듈을 하나 만들겠습니다. 그리고 아래의 코드를 작성합니다.

```python
class SysTrader():
    def __init__(self):
        """자동투자시스템 메인 클래스
        """
        self.hello()
    
    def hello(self):
        print("Hello World!")


if __name__ == "__main__":
    trader = SysTrader()
```

이렇게 클래스 하나를 선언하고 클래스의 객체를 생성하고 `hello()` 함수를 호출하여 똑같이 `Hello World!`를 출력했습니다. 앞으로 이 `SysTrader` 클래스를 차근차근 이름값 하게 만들어 보겠습니다.

## 로거 (Logger) 준비하기

로거는 시스템이 동작하는 동안 발생하는 정보를 기록하기 위한 모듈입니다. 단순히 `print()` 함수를 써서 출력하는 것보다 로거를 쓰는 것이 정보를 콘솔, 파일로 관리할 수 있어서 효과적입니다. 또한 로거는 출력할 정보에 레벨 (Level)을 부여하여 정보의 중요 정도를 정할 수 있습니다.

이제 시스템에 로거를 추가해 보겠습니다.

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from logging.handlers import TimedRotatingFileHandler


class SysTrader():
    def __init__():
        """자동투자시스템 메인 클래스
        """
        pass


if __name__ == "__main__":
    # --------------------------------------------------
    # 로거 (Logger) 준비하기
    # --------------------------------------------------
    # 로그 파일 핸들러
    fh_log = TimedRotatingFileHandler('logs/log', when='midnight', encoding='utf-8', backupCount=120)
    fh_log.setLevel(logging.DEBUG)

    # 콘솔 핸들러
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)

    # 로깅 포멧 설정
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
    fh_log.setFormatter(formatter)
    sh.setFormatter(formatter)

    # 로거 생성 및 핸들러 등록
    logger = logging.getLogger('systrading')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh_log)
    logger.addHandler(sh)

    # --------------------------------------------------
    # 자동투자시스템 시작
    # --------------------------------------------------
    trader = SysTrader()
```

여기서는 로그를 파일과 콘솔에 출력합니다. 이를 위해 먼저 `logging` 모듈을 임포트합니다. 그리고 일별로 로그파일을 관리하기 위해 `TimedRotatingFileHandler` 클래스를 임포트 했습니다. `TimedRotatingFileHandler`의 생성자 파라미터로 파일 경로, 새로운 파일을 생성할 기준 (여기서는 자정 `midnight`으로 설정했습니다.), 파일 인코딩, 최대 파일 개수 `backupCounting`을 정해줍니다. 이렇게 하면 현재 로그는 `logs/log` 파일에 출력되고, 파일이 새로 생성될때 이전에 쌓였던 로그는 `logs/log.2017-08-15`와 같은 이름의 파일로 생성됩니다.

콘솔에서도 로그를 확인하기 위해 `StreamHandler` 클래스도 사용합니다.

각 핸들러에 `setLevel()`을 호출하는데, 레벨의 개념을 간략히 설명하겠습니다.

로깅 레벨과 그 값은 다음과 같습니다.

|레벨|값|
|---|---|
|CRITICAL|50|
|ERROR|40|
|WARNING|30|
|INFO|20|
|DEBUG|10|
|NOTSET|0|

이 중에서 하나를 지정하여 사용합니다. (자신만의 레벨을 만들수도 있지만, 미리 정의되어 있는 것을 사용하시는 것을 권장합니다.) 로깅 핸들러는 지정한 레벨보다 값이 높은 레벨의 로그들을 출력합니다. 주로 `DEBUG`, `INFO`, `ERROR`를 사용합니다.

이렇게 준비한 핸들러들을 `logger`에 등록합니다. 코드에서 볼 수 있듯이, 로거 수준에서 레벨을 지정할 수도 있습니다. 로그를 남기는 방법은 다음과 같습니다.

- `DEBUG` 레벨 로그: `logger.debug()`
- `INFO` 레벨 로그: `logger.info()`
- `ERROR` 레벨 로그: `logger.error()`

## 키움증권 API 컨트롤 준비하기 

## 동기적으로 API 호출하기

키움증권 API는 시세조회, 관심종목조회, 조건검색 등의 대부분 TR 조회를 아울러 1초당 5회로 제한하고 있습니다. 즉 TR 요청을 동시에 보내지 않고 0.2초 간격으로 순차적(동기적)으로 보내는 것이 좋습니다.

이를 위해 본 튜토리얼에서는 파이썬의 고급 기능을 활용하여 요청들을 줄을 세우고, 0.2초의 간격으로 하나씩 처리하는 자료구조와 프로세스를 쓰레드로 구현합니다.

> 큐(Queue)는 선입선출(FIFO, First In First Out) 자료구조 입니다.
![](img/요청큐.png) 

> 쓰레드는 독자적으로 알고리즘을 수행하는 프로그램 속의 작은 독립적인 프로그램이라고 생각하시면 됩니다. 수행이 독립적으로 일어나기는 하지만 쓰레드 간에 데이터를 공유할 수는 있습니다.

구현은 다음과 같은 단계로 진행됩니다.

- 단계 1. `RequestThreadWorker` 클래스 구현
- 단계 2. `SysTrader` 클래스의 `__init__()` 함수에서 `RequestThreadWorker` 클래스의 객체 생성, 요청 쓰레드 객체 생성, 요청 쓰레드에 생성한 `RequestThreadWorker` 클래스의 객체 할당, 요청 쓰레드 객체 실행
- 단계 3. `SyncRequestDecorator` 데코레이터 클래스 구현
- 단계 4. 키움증권 API 요청 및 콜백 함수에 `SyncRequestDecorator` 데코레이터 설정

### 단계 1

`RequestThreadWorker`는 요청들을 줄세울 수 있도록 큐(Queue) 자료구조를 가지고, 여기서 요청들을 하나씩 빼내서 0.2초 이상의 간격으로 호출하는 프로세스를 가지고 있습니다.

```python
from collections import deque
from threading import Lock


class RequestThreadWorker(QObject):
    def __init__(self):
        """요청 쓰레드
        """
        super().__init__()
        self.request_queue = deque()  # 요청 큐
        self.request_thread_lock = Lock()

        # 간혹 요청에 대한 결과가 콜백으로 오지 않음
        # 마지막 요청을 저장해 뒀다가 일정 시간이 지나도 결과가 안오면 재요청
        self.retry_timer = None

    def retry(self, request):
        logger.debug("키움 함수 재시도: %s %s %s" % (request[0].__name__, request[1], request[2]))
        self.request_queue.appendleft(request)

    def run(self):
        while True:
            # 큐에 요청이 있으면 하나 뺌
            # 없으면 블락상태로 있음
            try:
                request = self.request_queue.popleft()
            except IndexError as e:
                time.sleep(요청주기)
                continue

            # 요청 실행
            logger.debug("키움 함수 실행: %s %s %s" % (request[0].__name__, request[1], request[2]))
            request[0](trader, *request[1], **request[2])

            # 요청에대한 결과 대기
            if not self.request_thread_lock.acquire(blocking=True, timeout=5):
                # 요청 실패
                time.sleep(요청주기)
                self.retry(request)  # 실패한 요청 재시도

            time.sleep(요청주기)  # 0.2초 이상 대기 후 마무리
```

`__init__()` 함수는 `RequestThreadWorker` 클래스의 객체가 초기화될 때 실행됩니다. 여기서 `request_queue` 속성를 `deque` 객체로 할당합니다. 이 속성에 요청을 넣으면 

### 단계 2

`SysTrader` 클래스의 `__init__()` 함수에서 `RequestThreadWorker`를 실행할 요청 쓰레드인 `request_thread` 속성을 생성합니다. `RequestThreadWorker` 클래스의 객체를 `request_thread`에 할당하고, 요청 쓰레드가 시작될 때 `RequestThreadWorker`의 `run()` 함수가 실행되도록 설정합니다. 최종적으로 요청쓰레드를 시작합니다.

```python
class SysTrader(QObject):
    def __init__(self):
        (중략)
        
        # 요청 쓰레드
        self.request_thread_worker = RequestThreadWorker()
        self.request_thread = QThread()
        self.request_thread_worker.moveToThread(self.request_thread)
        self.request_thread.started.connect(self.request_thread_worker.run)
        self.request_thread.start()
```

> `QThread` 클래스는 Qt 애플리케이션에서 사용하는 쓰레드 구현체입니다.


### 단계 3

키움증권 API의 요청 결과는 대부분 콜백 함수로 전달됩니다. 그러므로 요청을 동기적으로 하기 위해서는 이전에 호출한 요청의 결과가 콜백 함수로 전달될때까지 기다려야 합니다. 이를 위해 `SyncRequestDecorator` 클래스를 구현합니다. `SyncRequestDecorator` 클래스는 키움증권 API를 호출하는 요청 함수들에 적용할 데코레이터와 콜백 함수들에 적용할 데코레이터를 가집니다.

`kiwoom_sync_request()` 데코레이터에서는 요청 함수, 함수에 입력된 인자값들을 요청 큐(`request_queue`)에 넣어주는 역할을 합니다.

`kiwoom_sync_callback()`은 콜백 함수를 실행한 후 요청 쓰레드의 잠금을 해제합니다.

```python
class SyncRequestDecorator:
    """키움 API 비동기 함수 데코레이터
    """
    @staticmethod
    def kiwoom_sync_request(func):
        def func_wrapper(self, *args, **kwargs):
            self.request_thread_worker.request_queue.append((func, args, kwargs))
        return func_wrapper

    @staticmethod
    def kiwoom_sync_callback(func):
        def func_wrapper(self, *args, **kwargs):
            logger.debug("키움 함수 콜백: %s %s %s" % (func.__name__, args, kwargs))
            func(self, *args, **kwargs)  # 콜백 함수 호출
            if self.request_thread_worker.request_thread_lock.locked():
                self.request_thread_worker.request_thread_lock.release()  # 요청 쓰레드 잠금 해제
        return func_wrapper
```

### 단계 3

### 단계 4

## 로그인하기

이제 키움증권 API를 이용하여 투자 시스템에 로그인 해보겠습니다. 우선 Qt 애플리케이션을 생성하고 키움증권 API의 컨트롤 객체를 생성합니다. 여기서 Qt 관련 클래스들을 자세히 설명하지는 않겠습니다. 이들 클래스에 대한 깊은 이해가 없어도 자동투자 시스템을 개발하기에 무리가 없습니다.

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication


class SysTrader(QObject):
    def __init__():
        """자동투자시스템 메인 클래스
        """
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.OnEventConnect.connect(self.kiwoom_OnEventConnect)  # 로그인 결과를 받을 콜백함수 연결

        self.kiwoom_CommConnect()  # 로그인

    # -------------------------------------
    # 로그인 관련함수
    # -------------------------------------
    @Decorator.kiwoom_async_request
    def kiwoom_CommConnect(self):
        """로그인 요청
        키움증권 로그인창 띄워주고, 자동로그인 설정시 바로 로그인 진행됨.
        OnEventConnect()으로 콜백 전달됨.
        :param kwargs:
        :return: 1: 로그인 요청 성공, 0: 로그인 요청 실패
        """
        lRet = self.kiwoom.dynamicCall("CommConnect()")
        return lRet

    @Decorator.kiwoom_async_callback
    def kiwoom_OnEventConnect(self, nErrCode):
        """로그인 결과 수신
        :param nErrCode: 0: 로그인 성공, 100: 사용자 정보교환 실패, 101: 서버접속 실패, 102: 버전처리 실패
        :param kwargs:
        :return:
        """
        if nErrCode == 0:
            logger.debug("로그인 성공")
        elif nErrCode == 100:
            logger.debug("사용자 정보교환 실패")
        elif nErrCode == 101:
            logger.debug("서버접속 실패")
        elif nErrCode == 102:
            logger.debug("버전처리 실패")


if __name__ == "__main__":
    (중략)

    # --------------------------------------------------
    # 자동투자시스템 시작
    # --------------------------------------------------
    app = QApplication(sys.argv)  # Qt 애플리케이션 생성
    trader = SysTrader()  # QObject를 상속하는 자동투자시스템 객체 생성
    sys.exit(app.exec_())
```

`kiwoom_CommConnect()` 함수에서 키움증권 API 컨트롤을 통해 `CommConnect()` API를 호출하여 로그인 요청을 합니다. 처음에는 키움증권 로그인 창이 나타나고 아이디, 비밀번호 등을 입력하여 로그인합니다. 로그인 결과는 콜백으로 `kiwoom_OnEventConnect()` 함수에 전달됩니다. 이때 파라미터로 넘어오는 `nErrCode`의 값으로 로그인 결과를 판단합니다. 이 값이 `0`일 경우 로그인 성공입니다.

자동로그인을 설정해 놓은 경우 아이디, 비밀번호 입력 없이 자동으로 로그인이 진행되고, 그 결과가 콜백 함수로 들어옵니다.

## 계좌 확인하기

키움증권 API에 로그인을 했으면 이제 계좌의 잔고를 확인해 보겠습니다. 다음 스텝으로 구현합니다.

- 단계 1. `SysTrader` 클래스에 `kiwoom_SetInputValue()` 함수 추가
- 단계 2. ``

### 단계 1

먼저 다음 함수를 `SysTrader` 클래스에 추가합니다.

```python
    def kiwoom_SetInputValue(self, sID, sValue):
        """
        :param sID:
        :param sValue:
        :return:
        """
        res = self.kiwoom.dynamicCall("SetInputValue(QString, QString)", [sID, sValue])
        return res

    def kiwoom_CommRqData(self, sRQName, sTrCode, nPrevNext, sScreenNo):
        """

        :param sRQName:
        :param sTrCode:
        :param nPrevNext:
        :param sScreenNo:
        :return:
        """
        res = self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                      [sRQName, sTrCode, nPrevNext, sScreenNo])
        return res

    @Decorator.kiwoom_async_request
    def kiwoom_TR_OPW00001_예수금상세현황요청(self, 계좌번호, **kwargs):
        """계좌수익률요청
        :param 계좌번호: 계좌번호
        :param kwargs:
        :return:
        """
        res = self.kiwoom_SetInputValue("계좌번호", 계좌번호)
        res = self.kiwoom_CommRqData("예수금상세현황요청", "opw00001", 0, 화면번호_예수금상세현황)

    @Decorator.kiwoom_async_callback
    def kiwoom_OnReceiveTrData(self, sScrNo, sRQName, sTRCode, sRecordName, sPreNext, nDataLength, sErrorCode, sMessage, sSPlmMsg, **kwargs):
        """TR 요청에 대한 결과 수신
        데이터 얻어오기 위해 내부에서 GetCommData() 호출
          GetCommData(
          BSTR strTrCode,   // TR 이름
          BSTR strRecordName,   // 레코드이름
          long nIndex,      // TR반복부
          BSTR strItemName) // TR에서 얻어오려는 출력항목이름
        :param sScrNo: 화면번호
        :param sRQName: 사용자 구분명
        :param sTRCode: TR이름
        :param sRecordName: 레코드 이름
        :param sPreNext: 연속조회 유무를 판단하는 값 0: 연속(추가조회)데이터 없음, 2:연속(추가조회) 데이터 있음
        :param nDataLength: 사용안함
        :param sErrorCode: 사용안함
        :param sMessage: 사용안함
        :param sSPlmMsg: 사용안함
        :param kwargs:
        :return:
        """
    
        if sRQName == "예수금상세현황요청":
            self.int_주문가능금액 = int(self.kiwoom_GetCommData(sTRCode, sRQName, 0, "주문가능금액"))
            logger.debug("주문가능금액: %s" % (self.int_주문가능금액,))
```

먼저 `계좌번호`를 `SetInputValue()` 함수로 입력하고, `예수금상세현황요청`을 `CommRqData()` 함수로 호출합니다. 이 요청에 대한 결과는 `OnReceiveTrData()` 콜백 함수를 통해 확인할 수 있습니다.

이 콜백 함수를 키움증권 API 컨트롤에 연결해 주어야 합니다.

```python
    def __init__():
        """자동투자시스템 메인 클래스
        """
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.OnEventConnect.connect(self.kiwoom_OnEventConnect)  # 로그인 결과를 받을 콜백함수 연결
        self.kiwoom.OnReceiveTrData.connect(self.kiwoom_OnReceiveTrData)

        self.kiwoom_CommConnect()  # 로그인

```

## 코스피/코스닥 차트 읽어오기

### 강세장/약세장 분석하기

## 실시간 종목검색

## 종목 차트 읽어오기

### 일봉/분봉 차트를 활용한 매수/매도 포지셔닝하기

## 주문하기

# 주식 데이터 분석

## 주식 차트 그리기

## 

# 딥러닝을 이용한 자동투자 시뮬레이션 맛보기


