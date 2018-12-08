#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import re


# --------------------------------------------------------
# 문자열 처리 유틸
# --------------------------------------------------------
def 현재가_부호제거(현재가):
    return re.sub(r'\+|\-', '', 현재가)


# --------------------------------------------------------
# 시간 관련 유틸
# --------------------------------------------------------
FORMAT_DATE = "%Y%m%d"
FORMAT_DATETIME = "%Y%m%d%H%M%S"
FORMAT_MONTH = "%Y/%m"
FORMAT_MONTHDAY = "%m/%d"


import time
from pytz import timezone

def get_today():
    dt = datetime.datetime.fromtimestamp(time.time(), timezone('Asia/Seoul'))
    date = dt.date()
    return date


def get_str_today():
    str_today = get_today().strftime(FORMAT_DATE)
    return str_today


def get_str_month():
    str_month = get_today().strftime(FORMAT_MONTH)
    return str_month


def 날짜_오늘():
    return get_str_today()


def 날짜_5일전():
    date_today = datetime.date.today()
    str_d5 = (date_today - datetime.timedelta(days=7)).strftime(FORMAT_DATE)
    return str_d5


def 요일():
    """
    :return: 0-4 평일, 5-6 주말
    """
    date_today = datetime.date.today()
    int_week = date_today.weekday()
    return int_week


def 시분():
    dt_now = datetime.datetime.now()
    int_hour = dt_now.hour
    int_minute = dt_now.minute
    return int_hour, int_minute


# --------------------------------------------------------
# 변환 관련 유틸
# --------------------------------------------------------
def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


dict_conv = {
    '종목코드': ('code', str),
    '업종코드': ('code', str),
    '종목명': ('name', str),
    '회사명': ('name', str),
    '체결시간': ('time', int),
    '일자': ('date', int),
    '시가': ('open', float),
    '고가': ('high', float),
    '저가': ('low', float),
    '종가': ('close', float),
    '거래량': ('volume', float),
}


def convert_kv(d):
    _d = {}
    for k, v in d.items():
        if k in dict_conv:
            newk, vtype = dict_conv[k]
            _d[newk] = vtype(v)
        else:
            _d[k] = v
    return _d