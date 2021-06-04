#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import argparse
import subprocess

import win32com.client
from pywinauto import application

from quantylab.systrader import util


class Creon:
    def __init__(self, account_no=''):
        self.obj_CpUtil_CpCybos = win32com.client.Dispatch('CpUtil.CpCybos')
        self.obj_CpUtil_CpCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
        self.obj_CpSysDib_StockChart = win32com.client.Dispatch('CpSysDib.StockChart')
        self.obj_CpTrade_CpTdUtil = win32com.client.Dispatch('CpTrade.CpTdUtil')
        self.obj_CpSysDib_MarketEye = win32com.client.Dispatch('CpSysDib.MarketEye')
        self.obj_CpSysDib_CpSvr7238 = win32com.client.Dispatch('CpSysDib.CpSvr7238')
        self.obj_CpTrade_CpTdNew5331B = win32com.client.Dispatch('CpTrade.CpTdNew5331B')
        self.obj_CpTrade_CpTdNew5331A = win32com.client.Dispatch('CpTrade.CpTdNew5331A')
        self.obj_CpSysDib_CpSvr7254 = win32com.client.Dispatch('CpSysDib.CpSvr7254')
        self.obj_CpSysDib_CpSvr8548 = win32com.client.Dispatch('CpSysDib.CpSvr8548')
        self.obj_CpTrade_CpTd0311 = win32com.client.Dispatch('CpTrade.CpTd0311')
        self.obj_CpTrade_CpTd5341 = win32com.client.Dispatch('CpTrade.CpTd5341')
        self.obj_CpTrade_CpTd6033 = win32com.client.Dispatch('CpTrade.CpTd6033')
        
        # contexts
        self.stockcur_handlers = {}  # 주식/업종/ELW시세 subscribe event handlers

    def connect(self, id_, pwd, pwdcert, trycnt=300):
        if not self.connected():
            app = application.Application()
            app.start(
                'C:\\CREON\\STARTER\\coStarter.exe /prj:cp /id:{id} /pwd:{pwd} /pwdcert:{pwdcert} /autostart'.format(
                    id=id_, pwd=pwd, pwdcert=pwdcert
                )
            )

        cnt = 0
        while not self.connected():
            if cnt > trycnt:
                return False
            time.sleep(1)
            cnt += 1
        return True

    def connected(self):
        tasklist = subprocess.check_output('TASKLIST')
        if b"DibServer.exe" in tasklist and b"CpStart.exe" in tasklist:
            return self.obj_CpUtil_CpCybos.IsConnect != 0
        return False

    def disconnect(self):
        plist = [
            'coStarter',
            'CpStart',
            'DibServer',
        ]
        for p in plist:
            os.system('wmic process where "name like \'%{}%\'" call terminate'.format(p))
        return True

    def wait(self):
        remain_time = self.obj_CpUtil_CpCybos.LimitRequestRemainTime
        remain_count = self.obj_CpUtil_CpCybos.GetLimitRemainCount(1)
        if remain_count <= 3:
            time.sleep(remain_time / 1000)

    def request(self, obj, data_fields, header_fields=None, cntidx=0, n=None):
        def process():
            obj.BlockRequest()

            status = obj.GetDibStatus()
            msg = obj.GetDibMsg1()
            if status != 0:
                return None

            cnt = obj.GetHeaderValue(cntidx)
            data = []
            for i in range(cnt):
                dict_item = {k: obj.GetDataValue(j, cnt-1-i) for j, k in data_fields.items()}
                data.append(dict_item)
            return data

        # 연속조회 처리
        data = process()
        while obj.Continue:
            self.wait()
            _data = process()
            if len(_data) > 0:
                data = _data + data
                if n is not None and n <= len(data):
                    break
            else:
                break

        result = {'data': data}
        if header_fields is not None:
            result['header'] = {k: obj.GetHeaderValue(i) for i, k in header_fields.items()}

        return result

    def get_stockcodes(self, code):
        """
        code: kospi=1, kosdaq=2
        market codes:
            typedefenum{
            [helpstring("구분없음")]CPC_MARKET_NULL= 0, 
            [helpstring("거래소")]   CPC_MARKET_KOSPI= 1, 
            [helpstring("코스닥")]   CPC_MARKET_KOSDAQ= 2, 
            [helpstring("K-OTC")] CPC_MARKET_FREEBOARD= 3, 
            [helpstring("KRX")]       CPC_MARKET_KRX= 4,
            [helpstring("KONEX")] CPC_MARKET_KONEX= 5,
            }CPE_MARKET_KIND; 
        """
        res = self.obj_CpUtil_CpCodeMgr.GetStockListByMarket(code)
        return res

    def get_stockstatus(self, code):
        """
        code 에해당하는주식상태를반환한다

        code : 주식코드
        return :
        typedefenum {
        [helpstring("정상")]   CPC_CONTROL_NONE   = 0,
        [helpstring("주의")]   CPC_CONTROL_ATTENTION= 1,
        [helpstring("경고")]   CPC_CONTROL_WARNING= 2,
        [helpstring("위험예고")]CPC_CONTROL_DANGER_NOTICE= 3,
        [helpstring("위험")]   CPC_CONTROL_DANGER= 4,
        }CPE_CONTROL_KIND;
        typedefenum   {
        [helpstring("일반종목")]CPC_SUPERVISION_NONE= 0,
        [helpstring("관리")]   CPC_SUPERVISION_NORMAL= 1,
        }CPE_SUPERVISION_KIND;
        typedefenum   {
        [helpstring("정상")]   CPC_STOCK_STATUS_NORMAL= 0,
        [helpstring("거래정지")]CPC_STOCK_STATUS_STOP= 1,
        [helpstring("거래중단")]CPC_STOCK_STATUS_BREAK= 2,
        }CPE_SUPERVISION_KIND;
        """
        if not code.startswith('A'):
            code = 'A' + code
        return {
            'control': self.obj_CpUtil_CpCodeMgr.GetStockControlKind(code),
            'supervision': self.obj_CpUtil_CpCodeMgr.GetStockSupervisionKind(code),
            'status': self.obj_CpUtil_CpCodeMgr.GetStockStatusKind(code),
        }

    def get_stockfeatures(self, code):
        """
        https://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=284&seq=11&page=1&searchString=%EA%B1%B0%EB%9E%98%EC%A0%95%EC%A7%80&p=8841&v=8643&m=9505
        """
        if not code.startswith('A'):
            code = 'A' + code
        stock = {
            'name': self.obj_CpUtil_CpCodeMgr.CodeToName(code),
            'marginrate': self.obj_CpUtil_CpCodeMgr.GetStockMarginRate(code),
            'unit': self.obj_CpUtil_CpCodeMgr.GetStockMemeMin(code),
            'industry': self.obj_CpUtil_CpCodeMgr.GetStockIndustryCode(code),
            'market': self.obj_CpUtil_CpCodeMgr.GetStockMarketKind(code),
            'control': self.obj_CpUtil_CpCodeMgr.GetStockControlKind(code),
            'supervision': self.obj_CpUtil_CpCodeMgr.GetStockSupervisionKind(code),
            'status': self.obj_CpUtil_CpCodeMgr.GetStockStatusKind(code),
            'capital': self.obj_CpUtil_CpCodeMgr.GetStockCapital(code),
            'fiscalmonth': self.obj_CpUtil_CpCodeMgr.GetStockFiscalMonth(code),
            'groupcode': self.obj_CpUtil_CpCodeMgr.GetStockGroupCode(code),
            'kospi200kind': self.obj_CpUtil_CpCodeMgr.GetStockKospi200Kind(code),
            'section': self.obj_CpUtil_CpCodeMgr.GetStockSectionKind(code),
            'off': self.obj_CpUtil_CpCodeMgr.GetStockLacKind(code),
            'listeddate': self.obj_CpUtil_CpCodeMgr.GetStockListedDate(code),
            'maxprice': self.obj_CpUtil_CpCodeMgr.GetStockMaxPrice(code),
            'minprice': self.obj_CpUtil_CpCodeMgr.GetStockMinPrice(code),
            'ydopen': self.obj_CpUtil_CpCodeMgr.GetStockYdOpenPrice(code),
            'ydhigh': self.obj_CpUtil_CpCodeMgr.GetStockYdHighPrice(code),
            'ydlow': self.obj_CpUtil_CpCodeMgr.GetStockYdLowPrice(code),
            'ydclose': self.obj_CpUtil_CpCodeMgr.GetStockYdClosePrice(code),
            'creditenabled': self.obj_CpUtil_CpCodeMgr.IsStockCreditEnable(code),
            'parpricechangetype': self.obj_CpUtil_CpCodeMgr.GetStockParPriceChageType(code),
            'spac': self.obj_CpUtil_CpCodeMgr.IsSPAC(code),
            'biglisting': self.obj_CpUtil_CpCodeMgr.IsBigListingStock(code),
            'groupname': self.obj_CpUtil_CpCodeMgr.GetGroupName(code),
            'industryname': self.obj_CpUtil_CpCodeMgr.GetIndustryName(code),
            'membername': self.obj_CpUtil_CpCodeMgr.GetMemberName(code),
        }

        _fields = [20, 21, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 116, 118, 120, 123, 124, 125, 127, 156]
        _keys = ['총상장주식수', '외국인보유비율', 'PER', '시간외매수잔량', '시간외매도잔량', 'EPS', '자본금', '액면가', '배당률', '배당수익률', '부채비율', '유보율', '자기자본이익률', '매출액증가율', '경상이익증가율', '순이익증가율', '투자심리', 'VR', '5일회전율', '4일종가합', '9일종가합', '매출액', '경상이익', '당기순이익', 'BPS', '영업이익증가율', '영업이익', '매출액영업이익률', '매출액경상이익률', '이자보상비율', '분기BPS', '분기매출액증가율', '분기영업이액증가율', '분기경상이익증가율', '분기순이익증가율', '분기매출액', '분기영업이익', '분기경상이익', '분기당기순이익', '분개매출액영업이익률', '분기매출액경상이익률', '분기ROE', '분기이자보상비율', '분기유보율', '분기부채비율', '프로그램순매수', '당일외국인순매수', '당일기관순매수', 'SPS', 'CFPS', 'EBITDA', '공매도수량', '당일개인순매수']
        self.obj_CpSysDib_MarketEye.SetInputValue(0, _fields)
        self.obj_CpSysDib_MarketEye.SetInputValue(1, code)
        self.obj_CpSysDib_MarketEye.BlockRequest()

        cnt_field = self.obj_CpSysDib_MarketEye.GetHeaderValue(0)
        if cnt_field > 0:
            for i in range(cnt_field):
                stock[_keys[i]] = self.obj_CpSysDib_MarketEye.GetDataValue(i, 0)
        return stock

    def get_chart(self, code, target='A', unit='D', n=None, date_from=None, date_to=None):
        """
        https://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=284&seq=102&page=1&searchString=StockChart&p=8841&v=8643&m=9505
        "전일대비"는 제공하지 않으므로 직접 계산해야 함
        target: 'A', 'U' == 종목, 업종
        unit: 'D', 'W', 'M', 'm', 'T' == day, week, month, min, tick
        return <dict>dict_chart
        """
        _fields = []
        _keys = []
        if unit == 'm':
            _fields = [0, 1, 2, 3, 4, 5, 6, 8, 9, 37]
            _keys = ['date', 'time', 'open', 'high', 'low', 'close', 'diff', 'volume', 'price', 'diffsign']
        else:
            _fields = [0, 2, 3, 4, 5, 6, 8, 9, 37]
            _keys = ['date', 'open', 'high', 'low', 'close', 'diff', 'volume', 'price', 'diffsign']

        if date_to is None:
            date_to = util.get_str_today()

        self.obj_CpSysDib_StockChart.SetInputValue(0, target+code) # 주식코드: A, 업종코드: U
        if n is not None:
            self.obj_CpSysDib_StockChart.SetInputValue(1, ord('2'))  # 0: ?, 1: 기간, 2: 개수
            self.obj_CpSysDib_StockChart.SetInputValue(4, n)  # 요청 개수
        if date_from is not None or date_to is not None:
            if date_from is not None and date_to is not None:
                self.obj_CpSysDib_StockChart.SetInputValue(1, ord('1'))  # 0: ?, 1: 기간, 2: 개수
            if date_from is not None:
                self.obj_CpSysDib_StockChart.SetInputValue(3, date_from)  # 시작일
            if date_to is not None:
                self.obj_CpSysDib_StockChart.SetInputValue(2, date_to)  # 종료일
        self.obj_CpSysDib_StockChart.SetInputValue(5, _fields)  # 필드
        self.obj_CpSysDib_StockChart.SetInputValue(6, ord(unit))
        self.obj_CpSysDib_StockChart.SetInputValue(9, ord('1')) # 0: 무수정주가, 1: 수정주가

        result = self.request(self.obj_CpSysDib_StockChart, dict(zip(range(len(_keys)), _keys)), cntidx=3, n=n)
        result = result['data']
        for dict_item in result:
            dict_item['code'] = code

            # type conversion
            dict_item['diffsign'] = chr(dict_item['diffsign'])
            for k in ['open', 'high', 'low', 'close', 'diff']:
                dict_item[k] = float(dict_item[k])
            for k in ['volume', 'price']:
                dict_item[k] = int(dict_item[k])

            # additional fields
            dict_item['diffratio'] = (dict_item['diff'] / (dict_item['close'] - dict_item['diff'])) * 100
        
        return result

    def get_shortstockselling(self, code, n=None):
        """
        종목별공매도추이
        """
        _keys = ['date', 'close', 'diff', 'diffratio', 'volume', 'short_volume', 'short_ratio', 'short_amount', 'avg_price', 'avg_price_ratio']

        self.obj_CpSysDib_CpSvr7238.SetInputValue(0, 'A'+code) 

        result = self.request(self.obj_CpSysDib_CpSvr7238, dict(zip(range(len(_keys)), _keys)), n=n)
        result = result['data']
        for dict_item in result:
            dict_item['code'] = code

        return result

    def get_balance(self, account):
        """
        매수가능금액
        """
        self.obj_CpTrade_CpTdUtil.TradeInit()
        self.obj_CpTrade_CpTdNew5331A.SetInputValue(0, account)
        self.obj_CpTrade_CpTdNew5331A.BlockRequest()
        v = self.obj_CpTrade_CpTdNew5331A.GetHeaderValue(10)
        return v

    def get_holdingstocks(self, account):
        """
        보유종목
        """
        self.obj_CpTrade_CpTdUtil.TradeInit()
        self.obj_CpTrade_CpTdNew5331B.SetInputValue(0, account)
        self.obj_CpTrade_CpTdNew5331B.SetInputValue(3, ord('1')) # 1: 주식, 2: 채권
        self.obj_CpTrade_CpTdNew5331B.BlockRequest()
        cnt = self.obj_CpTrade_CpTdNew5331B.GetHeaderValue(0)
        res = []
        for i in range(cnt):
            item = {
                'code': self.obj_CpTrade_CpTdNew5331B.GetDataValue(0, i),
                'name': self.obj_CpTrade_CpTdNew5331B.GetDataValue(1, i),
                'holdnum': self.obj_CpTrade_CpTdNew5331B.GetDataValue(6, i),
                'buy_yesterday': self.obj_CpTrade_CpTdNew5331B.GetDataValue(7, i),
                'sell_yesterday': self.obj_CpTrade_CpTdNew5331B.GetDataValue(8, i),
                'buy_today': self.obj_CpTrade_CpTdNew5331B.GetDataValue(10, i),
                'sell_today': self.obj_CpTrade_CpTdNew5331B.GetDataValue(11, i),
            }
            res.append(item)
        return res

    def get_investorbuysell(self, code, n=None):
        """
        투자자별 매매동향
        """
        _keys = ['date', 'ind', 'foreign', 'inst', 'fin', 'ins', 'trust', 'bank', 'fin_etc', 'fund', 'corp', 'foreign_etc', 'private_fund', 'country', 'close', 'diff', 'diffratio', 'volume', 'confirm']

        self.obj_CpSysDib_CpSvr7254.SetInputValue(0, 'A' + code)
        self.obj_CpSysDib_CpSvr7254.SetInputValue(1, 6)
        self.obj_CpSysDib_CpSvr7254.SetInputValue(4, ord('0'))
        self.obj_CpSysDib_CpSvr7254.SetInputValue(5, 0)
        self.obj_CpSysDib_CpSvr7254.SetInputValue(6, ord('1'))  # '1': 순매수량, '2': 추정금액(백만원)
        
        result = self.request(self.obj_CpSysDib_CpSvr7254, dict(zip(range(len(_keys)), _keys)), cntidx=1, n=n)
        result = result['data']
        for dict_item in result:
            dict_item['code'] = code
            dict_item['confirm'] = chr(dict_item['confirm'])

        return result

    def get_marketcap(self, target='2'):
        """
        시가총액비중
        0 - (string) 종목코드
        1 - (string) 종목명
        2 - (long) 현재가
        3 - (long) 대비
        4 - (float) 전일대비비율
        5 - (long) 거래량
        6 - (long) 시가총액(단위:억원)
        7 - (float) 시가총액비중
        8 - (float) 외인비중
        9 - (float) 지수영향
        10 - (float) 지수영향(%)
        11 - (float) 기여도
        """
        _keys = ['code', 'name', 'close', 'diff', 'diffratio', 'volume', '시가총액', '시가총액비중', '외인비중', '지수영향', '지수영향', '기여도']

        self.obj_CpSysDib_CpSvr8548.SetInputValue(0, ord(target))  # '1': KOSPI200, '2': 거래소전체, '4': 코스닥전체

        result = self.request(self.obj_CpSysDib_CpSvr8548, dict(zip(range(len(_keys)), _keys)))
        result = result['data']

        str_today = util.get_str_today()
        market = ''
        if target == '2':
            market = 'kospi'
        elif target == '4':
            market = 'kosdaq'
        for dict_item in result:
            dict_item['code'] = dict_item['code'][1:]
            for k in ['close', 'diff', 'volume', '시가총액']:
                dict_item[k] = int(dict_item[k])
            for k in ['diffratio', '시가총액비중', '외인비중', '지수영향', '지수영향', '기여도']:
                dict_item[k] = float(dict_item[k])
            dict_item['market'] = market
            dict_item['date'] = str_today

        return result

    def subscribe_stockcur(self, code, cb):
        # https://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=285&seq=16&page=3&searchString=%EC%8B%A4%EC%8B%9C%EA%B0%84&p=&v=&m=
        if not code.startswith('A'):
            code = 'A' + code
        if code in self.stockcur_handlers:
            return
        obj = win32com.client.Dispatch('DsCbo1.StockCur')
        obj.SetInputValue(0, code)
        handler = win32com.client.WithEvents(obj, StockCurEventHandler)
        handler.set_attrs(obj, cb)
        self.stockcur_handlers[code] = obj
        obj.Subscribe()

    def unsubscribe_stockcur(self, code=None):
        lst_code = []
        if code is not None:
            if not code.startswith('A'):
                code = 'A' + code
            if code not in self.stockcur_handlers:
                return
            lst_code.append(code)
        else:
            lst_code = list(self.stockcur_handlers.keys()).copy()
        for code in lst_code:
            obj = self.stockcur_handlers[code]
            obj.Unsubscribe()
            del self.stockcur_handlers[code]

    def init_trade(self):
        if self.obj_CpTrade_CpTdUtil.TradeInit(0) != 0:
            print("TradeInit failed.", file=sys.stderr)
            return
        account_no = self.obj_CpTrade_CpTdUtil.AccountNumber[0]  # 계좌번호
        account_gflags = self.obj_CpTrade_CpTdUtil.GoodsList(account_no, 1)  # 주식상품 구분
        return account_no, account_gflags

    def order(self, action, code, amount):
        if not code.startswith('A'):
            code = 'A' + code
        account_no, account_gflags = self.init_trade()
        self.obj_CpTrade_CpTd0311.SetInputValue(0, action)  # 1: 매도, 2: 매수
        self.obj_CpTrade_CpTd0311.SetInputValue(1, account_no)  # 계좌번호
        self.obj_CpTrade_CpTd0311.SetInputValue(2, account_gflags[0])  # 상품구분
        self.obj_CpTrade_CpTd0311.SetInputValue(3, code)  # 종목코드
        self.obj_CpTrade_CpTd0311.SetInputValue(4, amount)  # 매수수량
        self.obj_CpTrade_CpTd0311.SetInputValue(8, '03')  # 시장가
        result = self.obj_CpTrade_CpTd0311.BlockRequest()
        if result != 0:
            print('buy request failed.', file=sys.stderr)
        status = self.obj_CpTrade_CpTd0311.GetDibStatus()
        msg = self.obj_CpTrade_CpTd0311.GetDibMsg1()
        if status != 0:
            print('buy failed. {}'.format(msg), file=sys.stderr)

    def buy(self, code, amount):
        return self.order('2', code, amount)

    def sell(self, code, amount):
        return self.order('1', code, amount)

    def get_trade_history(self):
        account_no, account_gflags = self.init_trade()
        self.obj_CpTrade_CpTd5341.SetInputValue(0, account_no)
        self.obj_CpTrade_CpTd5341.SetInputValue(1, account_gflags[0])  # 상품구분

        _fields = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 22, 24]
        _keys = [
            '상품관리구분코드', '주문번호', '원주문번호', '종목코드', '종목이름', 
            '주문내용', '주문호가구분코드내용', '주문수량', '주문단가', '총체결수량', 
            '체결수량', '체결단가', '확인수량', '정정취소구분내용 ', '거부사유내용', 
            '채권매수일', '거래세과세구분내용', '현금신용대용구분내용', '주문입력매체코드내용', 
            '정정취소가능수량', '매매구분',
        ]

        result = self.request(self.obj_CpTrade_CpTd5341, dict(zip(_fields, _keys)), cntidx=6)
        return result

    def get_balance(self):
        """
        0 - (string) 계좌번호
        1 - (string) 상품관리구분코드
        2 - (long) 요청건수[default:14] - 최대 50개
        3 - (string) 수익률구분코드 - ( "1" : 100% 기준, "2": 0% 기준)
        """
        account_no, account_gflags = self.init_trade()
        self.obj_CpTrade_CpTd6033.SetInputValue(0, account_no)
        self.obj_CpTrade_CpTd6033.SetInputValue(1, account_gflags[0])
        self.obj_CpTrade_CpTd6033.SetInputValue(3, '2')

        header_fields = {
            0: '계좌명',
            1: '결제잔고수량',
            2: '체결잔고수량',
            3: '총평가금액',
            4: '평가손익',
            6: '대출금액',
            7: '수신개수',
            8: '수익율',
        }

        data_fields = {
            0: '종목명',
            1: '신용구분',
            2: '대출일',
            3: '결제잔고수량',
            4: '결제장부단가',
            5: '전일체결수량',
            6: '금일체결수량',
            7: '체결잔고수량',
            9: '평가금액',
            10: '평가손익',
            11: '수익률',
            12: '종목코드',
            13: '주문구분',
            15: '매도가능수량',
            16: '만기일',
            17: '체결장부단가',
            18: '손익단가',
        }

        result = self.request(self.obj_CpTrade_CpTd6033, data_fields, header_fields=header_fields, cntidx=7)
        return result


class StockCurEventHandler:
    def set_attrs(self, obj, cb):
        self.obj = obj
        self.cb = cb

    def OnReceived(self):
        item = {
            'code': self.obj.GetHeaderValue(0),
            'name': self.obj.GetHeaderValue(1),
            'diffratio': self.obj.GetHeaderValue(2),
            'timestamp': self.obj.GetHeaderValue(3),  # 시간 형태 확인 필요
            'price_open': self.obj.GetHeaderValue(4),
            'price_high': self.obj.GetHeaderValue(5),
            'price_low': self.obj.GetHeaderValue(6),
            'bid_sell': self.obj.GetHeaderValue(7),
            'bid_buy': self.obj.GetHeaderValue(8),
            'cum_volume': self.obj.GetHeaderValue(9),  # 주, 거래소지수: 천주
            'cum_trans': self.obj.GetHeaderValue(10),
            'price': self.obj.GetHeaderValue(13),
            'contract_type': self.obj.GetHeaderValue(14),
            'cum_sellamount': self.obj.GetHeaderValue(15),
            'buy_sellamount': self.obj.GetHeaderValue(16),
            'contract_amount': self.obj.GetHeaderValue(17),
            'second': self.obj.GetHeaderValue(18),
            'price_type': chr(self.obj.GetHeaderValue(19)),  # 1: 동시호가시간 예상체결가, 2: 장중 체결가
            'market_flag': chr(self.obj.GetHeaderValue(20)),  # '1': 장전예상체결, '2': 장중, '4': 장후시간외, '5': 장후예상체결
            'premarket_volume': self.obj.GetHeaderValue(21),
            'diffsign': chr(self.obj.GetHeaderValue(22)),
            'LP보유수량':self.obj.GetHeaderValue(23),
            'LP보유수량대비':self.obj.GetHeaderValue(24),
            'LP보유율':self.obj.GetHeaderValue(25),
            '체결상태(호가방식)':self.obj.GetHeaderValue(26),
            '누적매도체결수량(호가방식)':self.obj.GetHeaderValue(27),
            '누적매수체결수량(호가방식)':self.obj.GetHeaderValue(28),
        }
        self.cb(item)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['connect', 'disconnect'])
    parser.add_argument('--id')
    parser.add_argument('--pwd')
    parser.add_argument('--pwdcert')
    args = parser.parse_args()

    c = Creon()

    if args.action == 'connect':
        c.connect(args.id, args.pwd, args.pwdcert)
    elif args.action == 'disconnect':
        c.disconnect()
