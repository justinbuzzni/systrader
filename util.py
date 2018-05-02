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


def 날짜_오늘():
    date_today = datetime.date.today()
    str_today = date_today.strftime(FORMAT_DATE)
    return str_today


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