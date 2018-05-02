#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
from collections import deque
from threading import Lock

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication

import numpy as np
import pandas as pd

import logging
from logging.handlers import TimedRotatingFileHandler

import util
import model


# 로그 파일 핸들러
fh_log = TimedRotatingFileHandler("logs/log", when="midnight", encoding="utf-8", backupCount=120)
fh_log.setLevel(logging.DEBUG)

# 콘솔 핸들러
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)

# 로깅 포멧 설정
formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
fh_log.setFormatter(formatter)
sh.setFormatter(formatter)

# 로거 생성
logger = logging.getLogger("systrader")
logger.setLevel(logging.DEBUG)
logger.addHandler(fh_log)
logger.addHandler(sh)

# 화면 번호
화면번호_조건검색 = "S"
화면번호_주식기본정보_PREFIX = "B"  # 종목코드 붙여서 화면번호 구성
화면번호_주식분봉차트조회_PREFIX = "C"  # 종목코드 붙여서 화면번호 구성
화면번호_주문_PREFIX = "O"  # 종목코드 붙여서 화면번호 구성
화면번호_계좌수익률 = "AP"  # Account Profit
화면번호_예수금상세현황 = "AB"  # Account Balance
화면번호_장시간 = "TIME"

# 상수
계좌번호 = "8091376411"  # 모의투자
# 계좌번호 = "5053546898"  # 실투자
종목별매수상한 = 1000000  # 종목별매수상한 백만원
매수수수료비율 = 0.00015  # 매도시 평단가에 곱해서 사용
매도수수료비율 = 0.00015 + 0.003  # 매도시 현재가에 곱해서 사용
연속요청대기초 = 0.25  # 초당 5회 제한이므로 최소한 0.2초 대기해야 함


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


class RequestThreadWorker(QObject):
    def __init__(self, caller):
        """요청 쓰레드
        """
        super().__init__()

        self.caller = caller

        self.request_queue = deque()
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
                time.sleep(연속요청대기초)
                continue

            # 요청에대한 결과 대기
            if not self.request_thread_lock.acquire(blocking=True, timeout=30):
                # 요청 실패
                time.sleep(연속요청대기초)
                self.retry(request)  # 실패한 요청 재시도

            # 요청 실행
            logger.debug("키움 함수 실행: %s %s %s" % (request[0].__name__, request[1], request[2]))
            request[0](self.caller, *request[1], **request[2])

            time.sleep(연속요청대기초)  # 0.2초 이상 대기 후 마무리


class Kiwoom(QObject):

    def __init__(self):
        """메인 객체
        """
        super().__init__()

        # 키움 시그널 연결
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.OnEventConnect.connect(self.kiwoom_OnEventConnect)
        self.kiwoom.OnReceiveTrData.connect(self.kiwoom_OnReceiveTrData)
        self.kiwoom.OnReceiveRealData.connect(self.kiwoom_OnReceiveRealData)
        self.kiwoom.OnReceiveConditionVer.connect(self.kiwoom_OnReceiveConditionVer)
        self.kiwoom.OnReceiveTrCondition.connect(self.kiwoom_OnReceiveTrCondition)
        self.kiwoom.OnReceiveRealCondition.connect(self.kiwoom_OnReceiveRealCondition)
        self.kiwoom.OnReceiveChejanData.connect(self.kiwoom_OnReceiveChejanData)
        self.kiwoom.OnReceiveMsg.connect(self.kiwoom_OnReceiveMsg)

        # 데이터
        self.set_stock2monitor = set()  # {종목코드}
        self.set_stock_ordered = set()  # {종목코드}

        # {종목코드: 종목기본정보}
        self.dict_stock = {}

        # {종목코드: 보유종목기본정보}
        # 보유종목기본정보: ["종목코드", "종목명", "현재가", "매입가", "보유수량"]
        self.dict_holding = {}

        # 차트
        self.dict_chart_minute = {}  # {종목코드: 분봉차트}
        self.dict_chart_day = {}  # {종목코드: 일봉차트}
        self.dict_chart_week = {}  # {종목코드: 주봉차트}
        self.dict_chart_month = {}  # {종목코드: 월봉차트}
        self.int_주문가능금액 = 0

        # 파라미터
        self.dict_param = {}

        # 콜백
        self.dict_callback = {}

        # 요청 쓰레드
        self.request_thread_worker = RequestThreadWorker(self)
        self.request_thread = QThread()
        self.request_thread_worker.moveToThread(self.request_thread)
        self.request_thread.started.connect(self.request_thread_worker.run)
        self.request_thread.start()

    def set_callback(self, req, cb):
        self.dict_callback[req] = cb

    def set_param(self, req, dict_param):
        self.dict_param[req] = dict_param

    # -------------------------------------
    # 로그인 관련함수
    # -------------------------------------
    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_CommConnect(self, **kwargs):
        """로그인 요청 (키움증권 로그인창 띄워줌. 자동로그인 설정시 바로 로그인 진행)
        OnEventConnect() 콜백
        :param kwargs:
        :return: 1: 로그인 요청 성공, 0: 로그인 요청 실패
        """
        lRet = self.kiwoom.dynamicCall("CommConnect()")
        return lRet

    def kiwoom_GetConnectState(self, **kwargs):
        """로그인 상태 확인
        OnEventConnect 콜백
        :param kwargs:
        :return: 0: 연결안됨, 1: 연결됨
        """
        lRet = self.kiwoom.dynamicCall("GetConnectState()")
        return lRet

    @SyncRequestDecorator.kiwoom_sync_callback
    def kiwoom_OnEventConnect(self, nErrCode, **kwargs):
        """로그인 결과 수신
        로그인 성공시 [조건목록 요청]GetConditionLoad() 실행
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

    # -------------------------------------
    # 조회 관련함수
    # -------------------------------------
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

    def kiwoom_GetRepeatCnt(self, sTRCode, sRQName):
        """

        :param sTRCode:
        :param sRQName:
        :return:
        """
        res = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", [sTRCode, sRQName])
        return res

    def kiwoom_GetCommData(self, sTRCode, sRQName, nIndex, sItemName):
        """

        :param sTRCode:
        :param sRQName:
        :param nIndex:
        :param sItemName:
        :return:
        """
        res = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)",
                                      [sTRCode, sRQName, nIndex, sItemName])
        return res

    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_TR_OPT10001_주식기본정보요청(self, strCode, **kwargs):
        """주식기본정보요청
        :param strCode:
        :param kwargs:
        :return:
        """
        res = self.kiwoom_SetInputValue("종목코드", strCode)
        res = self.kiwoom_CommRqData("주식기본정보", "OPT10001", 0, 화면번호_주식기본정보_PREFIX + strCode)

    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_TR_OPT10080_주식분봉차트조회(self, strCode, tick=1, fix=1, nPrevNext=0, **kwargs):
        """주식분봉차트조회
        :param strCode: 종목코드
        :param tick: 틱범위 (1:1분, 3:3분, 5:5분, 10:10분, 15:15분, 30:30분, 45:45분, 60:60분)
        :param fix: 수정주가구분 (0 or 1, 수신데이터 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락)
        :param nPrevNext:
        :param kwargs:
        :return:
        """
        res = self.kiwoom_SetInputValue("종목코드", strCode)
        res = self.kiwoom_SetInputValue("틱범위", str(tick))
        res = self.kiwoom_SetInputValue("수정주가구분", str(fix))
        res = self.kiwoom_CommRqData("주식분봉차트조회", "opt10080", nPrevNext, 화면번호_주식분봉차트조회_PREFIX + strCode)

    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_TR_OPT10085_계좌수익률요청(self, 계좌번호, **kwargs):
        """계좌수익률요청
        :param 계좌번호: 계좌번호
        :param kwargs:
        :return:
        """
        res = self.kiwoom_SetInputValue("계좌번호", 계좌번호)
        res = self.kiwoom_CommRqData("계좌수익률요청", "opt10085", 0, 화면번호_계좌수익률)

    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_TR_OPW00001_예수금상세현황요청(self, 계좌번호, **kwargs):
        """계좌수익률요청
        :param 계좌번호: 계좌번호
        :param kwargs:
        :return:
        """
        res = self.kiwoom_SetInputValue("계좌번호", 계좌번호)
        res = self.kiwoom_CommRqData("예수금상세현황요청", "opw00001", 0, 화면번호_예수금상세현황)

    @SyncRequestDecorator.kiwoom_sync_callback
    def kiwoom_OnReceiveTrData(self, sScrNo, sRQName, sTRCode, sRecordName, sPreNext, nDataLength, sErrorCode, sMessage,
                               sSPlmMsg, **kwargs):
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
            logger.debug("예수금상세현황요청: %s" % (self.int_주문가능금액,))
            if "예수금상세현황요청" in self.dict_callback:
                self.dict_callback["예수금상세현황요청"](self.int_주문가능금액)

        elif sRQName == "주식기본정보":
            cnt = self.kiwoom_GetRepeatCnt(sTRCode, sRQName)
            list_item_name = ["종목명", "현재가", "등락율", "거래량"]
            종목코드 = self.kiwoom_GetCommData(sTRCode, sRQName, 0, "종목코드")
            종목코드 = 종목코드.strip()
            dict_stock = self.dict_stock.get(종목코드, {})
            for item_name in list_item_name:
                item_value = self.kiwoom_GetCommData(sTRCode, sRQName, 0, item_name)
                item_value = item_value.strip()
                dict_stock[item_name] = item_value
            self.dict_stock[종목코드] = dict_stock
            logger.debug("주식기본정보: %s, %s" % (종목코드, dict_stock))
            if "주식기본정보" in self.dict_callback:
                self.dict_callback["주식기본정보"](dict_stock)

        elif sRQName == "시세표성정보":
            cnt = self.kiwoom_GetRepeatCnt(sTRCode, sRQName)
            list_item_name = ["종목명", "현재가", "등락률", "거래량"]
            dict_stock = {}
            for item_name in list_item_name:
                item_value = self.kiwoom_GetCommData(sTRCode, sRQName, 0, item_name)
                item_value = item_value.strip()
                dict_stock[item_name] = item_value
            if "시세표성정보" in self.dict_callback:
                self.dict_callback["시세표성정보"](dict_stock)

        elif sRQName == "주식분봉차트조회":
            cnt = self.kiwoom_GetRepeatCnt(sTRCode, sRQName)

            종목코드 = self.kiwoom_GetCommData(sTRCode, sRQName, 0, "종목코드")
            종목코드 = 종목코드.strip()

            dict_chart_tmp = {}  # 임시로 현재 조회된 차트만 저장
            done_범위조회 = False  # 파라미터 처리 플래그

            for nIdx in range(cnt):
                # list_item_name = ["현재가", "거래량", "체결시간", "시가", "고가",
                #                   "저가", "수정주가구분", "수정비율", "대업종구분", "소업종구분",
                #                   "종목정보", "수정주가이벤트", "전일종가"]
                list_item_name = ["체결시간", "시가", "고가", "저가", "현재가", "거래량"]
                dict_item = {}
                for item_name in list_item_name:
                    item_value = self.kiwoom_GetCommData(sTRCode, sRQName, nIdx, item_name)
                    item_value = item_value.strip()
                    dict_item[item_name] = item_value
                date_last = int(dict_item["체결시간"])

                # 범위조회 파라미터 처리
                dict_param = self.dict_param.get("주식분봉차트조회", {})
                date_from = int(dict_param.get("date_from", "000000000000"))
                date_to = int(dict_param.get("date_to", "999999999999"))

                if date_last > date_to:
                    continue
                elif date_last < date_from:
                    done_범위조회 = True
                    break

                # 아이템을 리스트에 추가
                for item_name, item_value in dict_item.items():
                    if item_name not in dict_chart_tmp:
                        dict_chart_tmp[item_name] = [item_value]
                    else:
                        dict_chart_tmp[item_name].append(item_value)

            # 이전에 조회된 차트 불러오기
            # 없으면 새로운 딕셔너리 저장
            if sPreNext == '0':
                dict_chart = {}
            else:
                dict_chart = self.dict_chart_minute.get(종목코드, {})

            # 조회 결과 차트에 추가
            for k, v in dict_chart_tmp.items():
                if type(v) is list:
                    dict_chart[k] = dict_chart.get(k, []) + v
                else:
                    dict_chart[k] = dict_chart.get(k, []) + [v]

            # 개수 파라미터처리
            dict_chart['cnt'] = cnt + dict_chart.get('cnt', 0)
            if dict_chart['cnt'] >= dict_param.get('size', float("inf")):
                done_범위조회 = True

            # 차트 업데이트
            self.dict_chart_minute[종목코드] = dict_chart

            if not done_범위조회 and cnt > 0:
                # 분봉차트 추가요청
                self.kiwoom_TR_OPT10080_주식분봉차트조회(종목코드, nPrevNext=2)
            else:
                # 연속조회 완료
                logger.debug("분봉차트 연속조회완료")
                self.dict_chart_minute[종목코드]["연속조회완료"] = True
                if '주식분봉차트조회' in self.dict_callback:
                    self.dict_callback['주식분봉차트조회'](dict_chart)

        elif sRQName == "계좌수익률요청":
            cnt = self.kiwoom_GetRepeatCnt(sTRCode, sRQName)
            for nIdx in range(cnt):
                list_item_name = ["종목코드", "종목명", "현재가", "매입가", "보유수량"]
                dict_holding = {item_name: self.kiwoom_GetCommData(sTRCode, sRQName, nIdx, item_name).strip() for
                                item_name in list_item_name}
                dict_holding["현재가"] = util.safe_cast(dict_holding["현재가"], int, 0)
                # 매입가를 총매입가로 키변경
                dict_holding["총매입가"] = util.safe_cast(dict_holding["매입가"], int, 0)
                dict_holding["보유수량"] = util.safe_cast(dict_holding["보유수량"], int, 0)
                dict_holding["수익"] = (dict_holding["현재가"] - dict_holding["총매입가"]) * dict_holding["보유수량"]
                종목코드 = dict_holding["종목코드"]
                self.dict_holding[종목코드] = dict_holding
                logger.debug("계좌수익: %s" % (dict_holding,))
            if '계좌수익률요청' in self.dict_callback:
                self.dict_callback['계좌수익률요청'](self.dict_holding)

    # -------------------------------------
    # 실시간 관련함수
    # -------------------------------------
    def kiwoom_OnReceiveRealData(self, sCode, sRealType, sRealData, **kwargs):
        """
        실시간 데이터 수신
          OnReceiveRealData(
          BSTR sCode,        // 종목코드
          BSTR sRealType,    // 리얼타입
          BSTR sRealData    // 실시간 데이터 전문
          )
        :param sCode: 종목코드
        :param sRealType: 리얼타입
        :param sRealData: 실시간 데이터 전문
        :param kwargs:
        :return:
        """
        logger.debug("REAL: %s %s %s" % (sCode, sRealType, sRealData))

        if sRealType == "주식체결":
            pass

    def kiwoom_SetRealReg(self, strScreenNo, strCodeList, strFidList, strOptType):
        """
        SetRealReg(
          BSTR strScreenNo,   // 화면번호
          BSTR strCodeList,   // 종목코드 리스트
          BSTR strFidList,  // 실시간 FID리스트
          BSTR strOptType   // 실시간 등록 타입, 0또는 1 (0은 교체 등록, 1은 추가 등록)
          )
        :param str:
        :return:
        """
        lRet = self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                                       [strScreenNo, strCodeList, strFidList, strOptType])
        return lRet

    # -------------------------------------
    # 조건검색 관련함수
    # GetConditionLoad(), OnReceiveConditionVer(), SendCondition(), OnReceiveRealCondition()
    # -------------------------------------
    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_GetConditionLoad(self, **kwargs):
        """
        조건검색의 조건목록 요청
        :return:
        """
        lRet = self.kiwoom.dynamicCall("GetConditionLoad()")
        return lRet

    @SyncRequestDecorator.kiwoom_sync_callback
    def kiwoom_OnReceiveConditionVer(self, lRet, sMsg, **kwargs):
        """
        조건검색의 조건목록 결과 수신
        GetConditionNameList() 실행하여 조건목록 획득.
        첫번째 조건 이용하여 [조건검색]SendCondition() 실행
        :param lRet:
        :param sMsg:
        :param kwargs:
        :return:
        """
        if lRet:
            sRet = self.kiwoom.dynamicCall("GetConditionNameList()")
            pairs = [idx_name.split('^') for idx_name in [cond for cond in sRet.split(';')]]
            if len(pairs) > 0:
                nIndex = pairs[0][0]
                strConditionName = pairs[0][1]
                self.kiwoom_SendCondition(strConditionName, nIndex)

    @SyncRequestDecorator.kiwoom_sync_request
    def kiwoom_SendCondition(self, strConditionName, nIndex, **kwargs):
        """
        조검검색 실시간 요청. OnReceiveConditionVer() 안에서 호출해야 함.
        실시간 요청이라도 OnReceiveTrCondition() 콜백 먼저 호출됨.
        조검검색 결과 변경시 OnReceiveRealCondition() 콜백 호출됨.
          SendCondition(
          BSTR strScrNo,    // 화면번호
          BSTR strConditionName,  // 조건식 이름
          int nIndex,     // 조건명 인덱스
          int nSearch   // 조회구분, 0:조건검색, 1:실시간 조건검색
          )
        :param strConditionName: 조건식 이름
        :param nIndex: 조건명 인덱스
        :param kwargs:
        :return: 1: 성공, 0: 실패
        """
        lRet = self.kiwoom.dynamicCall(
            "SendCondition(QString, QString, int, int)",
            [화면번호_조건검색, strConditionName, nIndex, 1]
        )
        return lRet

    @SyncRequestDecorator.kiwoom_sync_callback
    def kiwoom_OnReceiveTrCondition(self, sScrNo, strCodeList, strConditionName, nIndex, nNext, **kwargs):
        """
        조건검색 결과 수신
          OnReceiveTrCondition(
          BSTR sScrNo,    // 화면번호
          BSTR strCodeList,   // 종목코드 리스트
          BSTR strConditionName,    // 조건식 이름
          int nIndex,   // 조건명 인덱스
          int nNext   // 연속조회 여부
          )
        :param sScrNo: 화면번호
        :param strCodeList: 종목코드 리스트
        :param strConditionName: 조건식 이름
        :param nIndex: 조건명 인덱스
        :param nNext: 연속조회 여부
        :param kwargs:
        :return:
        """
        list_str_code = list(filter(None, strCodeList.split(';')))
        logger.debug("조건검색 결과: %s" % (list_str_code,))

        # 조검검색 결과를 종목 모니터링 리스트에 추가
        self.set_stock2monitor.update(set(list_str_code))

    def kiwoom_OnReceiveRealCondition(self, strCode, strType, strConditionName, strConditionIndex, **kwargs):
        """
        실시간 조건검색 결과 수신
          OnReceiveRealCondition(
          BSTR strCode,   // 종목코드
          BSTR strType,   //  이벤트 종류, "I":종목편입, "D", 종목이탈
          BSTR strConditionName,    // 조건식 이름
          BSTR strConditionIndex    // 조건명 인덱스
          )
        :param strCode: 종목코드
        :param strType: 이벤트 종류, "I":종목편입, "D", 종목이탈
        :param strConditionName: 조건식 이름
        :param strConditionIndex: 조건명 인덱스
        :param kwargs:
        :return:
        """
        logger.debug("실시간 조건검색: %s %s %s %s" % (strCode, strType, strConditionName, strConditionIndex))
        if strType == "I":
            # 모니터링 종목 리스트에 추가
            self.set_stock2monitor.add(strCode)
        elif strType == "D":
            # 모니터링 종목 리스트에서 삭제
            self.set_stock2monitor.remove(strCode)

    # -------------------------------------
    # 주문 관련함수
    # OnReceiveTRData(), OnReceiveMsg(), OnReceiveChejan()
    # -------------------------------------
    @SyncRequestDecorator.kiwoom_sync_callback
    def kiwoom_SendOrder(self, sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo,
                         **kwargs):
        """주문
        :param sRQName: 사용자 구분명
        :param sScreenNo: 화면번호
        :param sAccNo: 계좌번호 10자리
        :param nOrderType: 주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
        :param sCode: 종목코드
        :param nQty: 주문수량
        :param nPrice: 주문가격
        :param sHogaGb: 거래구분(혹은 호가구분)은 아래 참고
          00 : 지정가
          03 : 시장가
          05 : 조건부지정가
          06 : 최유리지정가
          07 : 최우선지정가
          10 : 지정가IOC
          13 : 시장가IOC
          16 : 최유리IOC
          20 : 지정가FOK
          23 : 시장가FOK
          26 : 최유리FOK
          61 : 장전시간외종가
          62 : 시간외단일가매매
          81 : 장후시간외종가
        :param sOrgOrderNo: 원주문번호입니다. 신규주문에는 공백, 정정(취소)주문할 원주문번호를 입력합니다.
        :param kwargs:
        :return:
        """
        logger.debug("주문: %s %s %s %s %s %s %s %s %s" % (
        sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo))
        lRet = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                       [sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb,
                                        sOrgOrderNo])

    @SyncRequestDecorator.kiwoom_sync_callback
    def kiwoom_OnReceiveMsg(self, sScrNo, sRQName, sTrCode, sMsg, **kwargs):
        """주문성공, 실패 메시지
        :param sScrNo: 화면번호
        :param sRQName: 사용자 구분명
        :param sTrCode: TR이름
        :param sMsg: 서버에서 전달하는 메시지
        :param kwargs:
        :return:
        """
        logger.debug("주문/잔고: %s %s %s %s" % (sScrNo, sRQName, sTrCode, sMsg))

    @SyncRequestDecorator.kiwoom_sync_callback
    def kiwoom_OnReceiveChejanData(self, sGubun, nItemCnt, sFIdList, **kwargs):
        """주문접수, 체결, 잔고발생시
        :param sGubun: 체결구분 접수와 체결시 '0'값, 국내주식 잔고전달은 '1'값, 파생잔고 전달은 '4"
        :param nItemCnt:
        :param sFIdList:
        "9201" : "계좌번호"
        "9203" : "주문번호"
        "9001" : "종목코드"
        "913" : "주문상태"
        "302" : "종목명"
        "900" : "주문수량"
        "901" : "주문가격"
        "902" : "미체결수량"
        "903" : "체결누계금액"
        "904" : "원주문번호"
        "905" : "주문구분"
        "906" : "매매구분"
        "907" : "매도수구분"
        "908" : "주문/체결시간"
        "909" : "체결번호"
        "910" : "체결가"
        "911" : "체결량"
        "10" : "현재가"
        "27" : "(최우선)매도호가"
        "28" : "(최우선)매수호가"
        "914" : "단위체결가"
        "915" : "단위체결량"
        "919" : "거부사유"
        "920" : "화면번호"
        "917" : "신용구분"
        "916" : "대출일"
        "930" : "보유수량"
        "931" : "매입단가"
        "932" : "총매입가"
        "933" : "주문가능수량"
        "945" : "당일순매수수량"
        "946" : "매도/매수구분"
        "950" : "당일총매도손일"
        "951" : "예수금"
        "307" : "기준가"
        "8019" : "손익율"
        "957" : "신용금액"
        "958" : "신용이자"
        "918" : "만기일"
        "990" : "당일실현손익(유가)"
        "991" : "당일실현손익률(유가)"
        "992" : "당일실현손익(신용)"
        "993" : "당일실현손익률(신용)"
        "397" : "파생상품거래단위"
        "305" : "상한가"
        "306" : "하한가"
        :param kwargs:
        :return:
        """
        logger.debug("체결/잔고: %s %s %s" % (sGubun, nItemCnt, sFIdList))
        if sGubun == '0':
            list_item_name = ["계좌번호", "주문번호", "관리자사번", "종목코드", "주문업무분류",
                              "주문상태", "종목명", "주문수량", "주문가격", "미체결수량",
                              "체결누계금액", "원주문번호", "주문구분", "매매구분", "매도수구분",
                              "주문체결시간", "체결번호", "체결가", "체결량", "현재가",
                              "매도호가", "매수호가", "단위체결가", "단위체결량", "당일매매수수료",
                              "당일매매세금", "거부사유", "화면번호", "터미널번호", "신용구분",
                              "대출일"]
            list_item_id = [9201, 9203, 9205, 9001, 912,
                            913, 302, 900, 901, 902,
                            903, 904, 905, 906, 907,
                            908, 909, 910, 911, 10,
                            27, 28, 914, 915, 938,
                            939, 919, 920, 921, 922,
                            923]
            dict_contract = {item_name: self.kiwoom_GetChejanData(item_id).strip() for item_name, item_id in
                             zip(list_item_name, list_item_id)}

            # 종목코드에서 'A' 제거
            종목코드 = dict_contract["종목코드"]
            if 'A' <= 종목코드[0] <= 'Z' or 'a' <= 종목코드[0] <= 'z':
                종목코드 = 종목코드[1:]
                dict_contract["종목코드"] = 종목코드

            # 종목을 대기 리스트에서 제거
            if 종목코드 in self.set_stock_ordered:
                self.set_stock_ordered.remove(종목코드)

            # 매수 체결일 경우 보유종목에 빈 dict 추가 (키만 추가하기 위해)
            if "매수" in dict_contract["주문구분"]:
                self.dict_holding[종목코드] = {}
            # 매도 체결일 경우 보유종목에서 제거
            else:
                self.dict_holding.pop(종목코드, None)

            logger.debug("체결: %s" % (dict_contract,))

        if sGubun == '1':
            list_item_name = ["계좌번호", "종목코드", "신용구분", "대출일", "종목명",
                              "현재가", "보유수량", "매입단가", "총매입가", "주문가능수량",
                              "당일순매수량", "매도매수구분", "당일총매도손일", "예수금", "매도호가",
                              "매수호가", "기준가", "손익율", "신용금액", "신용이자",
                              "만기일", "당일실현손익", "당일실현손익률", "당일실현손익_신용", "당일실현손익률_신용",
                              "담보대출수량", "기타"]
            list_item_id = [9201, 9001, 917, 916, 302,
                            10, 930, 931, 932, 933,
                            945, 946, 950, 951, 27,
                            28, 307, 8019, 957, 958,
                            918, 990, 991, 992, 993,
                            959, 924]
            dict_holding = {item_name: self.kiwoom_GetChejanData(item_id).strip() for item_name, item_id in
                            zip(list_item_name, list_item_id)}
            dict_holding["현재가"] = util.safe_cast(dict_holding["현재가"], int, 0)
            dict_holding["보유수량"] = util.safe_cast(dict_holding["보유수량"], int, 0)
            dict_holding["매입단가"] = util.safe_cast(dict_holding["매입단가"], int, 0)
            dict_holding["총매입가"] = util.safe_cast(dict_holding["총매입가"], int, 0)
            dict_holding["주문가능수량"] = util.safe_cast(dict_holding["주문가능수량"], int, 0)

            # 종목코드에서 'A' 제거
            종목코드 = dict_holding["종목코드"]
            if 'A' <= 종목코드[0] <= 'Z' or 'a' <= 종목코드[0] <= 'z':
                종목코드 = 종목코드[1:]
                dict_holding["종목코드"] = 종목코드

            # 보유종목 리스트에 추가
            self.dict_holding[종목코드] = dict_holding

            logger.debug("잔고: %s" % (dict_holding,))

    def kiwoom_GetChejanData(self, nFid):
        """
        OnReceiveChejan()이벤트 함수가 호출될때 체결정보나 잔고정보를 얻어오는 함수입니다.
        이 함수는 반드시 OnReceiveChejan()이벤트 함수가 호출될때 그 안에서 사용해야 합니다.
        :param nFid: 실시간 타입에 포함된FID
        :return:
        """
        res = self.kiwoom.dynamicCall("GetChejanData(int)", [nFid])
        return res
