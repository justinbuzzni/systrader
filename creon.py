import logging
from logging.handlers import TimedRotatingFileHandler

import sys
import win32com.client


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
logger = logging.getLogger("creon")
logger.setLevel(logging.DEBUG)
logger.addHandler(fh_log)
logger.addHandler(sh)


class Creon:
    def __init__(self):
        self.obj_CpCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
        self.obj_CpCybos = win32com.client.Dispatch('CpUtil.CpCybos')
        self.obj_StockChart = win32com.client.Dispatch("CpSysDib.StockChart")

    def creon_7400_주식차트조회(self):
        """
        http://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=284&seq=102&page=1&searchString=StockChart&p=8841&v=8643&m=9505
        :return:
        """
        b_connected = self.obj_CpCybos.IsConnect
        if b_connected == 0:
            logger.debug("연결 실패")
            return None

        self.obj_StockChart.SetInputValue(0, 'A035420')
        self.obj_StockChart.SetInputValue(1, ord('1'))  # 0: 개수, 1: 기간
        self.obj_StockChart.SetInputValue(2, '20180105')  # 종료일
        self.obj_StockChart.SetInputValue(3, '20180105')  # 시작일
        # self.obj_StockChart.SetInputValue(4, 100)  # 요청 개수
        self.obj_StockChart.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])  # 필드
        self.obj_StockChart.SetInputValue(6, ord('m'))  # 'D', 'W', 'M', 'm', 'T'
        self.obj_StockChart.BlockRequest()

        status = self.obj_StockChart.GetDibStatus()
        msg = self.obj_StockChart.GetDibMsg1()
        logger.debug("통신상태: {} {}".format(status, msg))
        if status != 0:
            return None

        cnt = self.obj_StockChart.GetHeaderValue(3)
        list_date = []
        list_open = []
        list_high = []
        list_low = []
        list_close = []
        list_volume = []
        for i in range(cnt):
            list_date.append(self.obj_StockChart.GetDataValue(0,i))
            list_open.append(self.obj_StockChart.GetDataValue(1, i))
            list_high.append(self.obj_StockChart.GetDataValue(2, i))
            list_low.append(self.obj_StockChart.GetDataValue(3, i))
            list_close.append(self.obj_StockChart.GetDataValue(4, i))
            list_volume.append(self.obj_StockChart.GetDataValue(5, i))
        dict_chart = {
            "체결일": list_date,
            "시가": list_open,
            "고가": list_high,
            "저가": list_low,
            "종가": list_close,
            "체결량": list_volume
        }
        logger.debug("차트: {}".format(dict_chart))

        return dict_chart


if __name__ == '__main__':
    creon = Creon()
    print(creon.creon_7400_주식차트조회())
