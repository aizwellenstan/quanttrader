#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Making identical historical data requests within 15 seconds.
Making six or more historical data requests for the same Contract, Exchange and Tick Type within two seconds.
Making more than 60 requests within any ten minute period.
"""
import os
import argparse
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pickle
from quanttrading2.event.event import EventType
from quanttrading2.event.live_event_engine import LiveEventEngine
from quanttrading2.brokerage.ib_brokerage import InteractiveBrokers

df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])

def log_event_handler(log_event):
    print(f'{log_event.timestamp}: {log_event.content}')

def historical_event_handler(bar_event):
    """
    local timezone based on tws setting
    """
    global df
    row_dict = {}
    row_dict['Open'] = bar_event.open_price
    row_dict['High'] = bar_event.high_price
    row_dict['Low'] = bar_event.low_price
    row_dict['Close'] = bar_event.close_price
    row_dict['Volume'] = bar_event.volume
    df1 = pd.DataFrame(row_dict, index=[bar_event.bar_start_time])
    df = pd.concat([df, df1], axis=0)

def run(args):
    global  df
    events_engine = LiveEventEngine()  # update ui
    broker = InteractiveBrokers(events_engine, 'DU0001')
    broker.reqid = 5000
    events_engine.register_handler(EventType.LOG, log_event_handler)
    events_engine.register_handler(EventType.BAR, historical_event_handler)
    events_engine.start()

    broker.connect('127.0.0.1', 7497, 0)

    # RTH stock 9:30~16:00; FUT 9:30~17:00, ES halt 16:15~16:30
    # 7.5h x 2 = 15 requests = 15*15 ~ 4min
    symbols = [
        'ESU0 FUT GLOBEX',
        'NQU0 FUT GLOBEX',
        'CLU0 FUT NYNEX',
        'HOU0 FUT NYMEX',
        'XBU0 FUT NYMEX',
        'SPY STK SMART',
        'QQQ STK SMART',
        'XLE STK SMART',
        'XLF STK SMART',
        'XLU STK SMART',
        'XLK STK SMART',
        'XLP STK SMART',
        'XLI STK SMART',
        'XLV STK SMART',
        'XLB STK SMART',
        'XLY STK SMART',
        'XLRE STK SMART',
        'XLC STK SMART'
    ]

    sym = 'AAPL STK SMART'
    end_date = datetime.strptime('20200811', '%Y%m%d')
    if 'STK' in sym:
        end_date = end_date - timedelta(hours=8)       # 16:00
    else:
        end_date = end_date - timedelta(hours=7)       # 17:00

    while end_date.hour >= 10:
        broker.request_historical_data(sym, end_date)
        end_date = end_date - timedelta(minutes=30)
        time.sleep(15)       # 15 seconds
        # TODO combine first

    broker.disconnect()
    events_engine.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Historical Downloader')
    parser.add_argument('--date', help='yyyymmdd')

    args = parser.parse_args()
    run(args)
