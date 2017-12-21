#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : helper.py
@desc    : 帮助在命令行下更好的使用
@time    : 17-12-21 下午8:34 
"""

import argparse
import sys

from web_cache import __version__, __description__


class Helper:

    def __init__(self):
        self._wcache_ip = '0.0.0.0'
        self._wcache_port = 6666

    def help(self):
        parser = argparse.ArgumentParser(description=__description__)
        parser.add_argument('-v', '--version', action='store_true', help='output version and exit')

        # web cache监听接口设置
        parser.add_argument('--ip', default='0.0.0.0', help='the interface of web cache can listen')
        parser.add_argument('--port', type=int, default=6666, help='the port of web cache can listen')

        # 获取参数
        args = parser.parse_args()

        if args.version:
            print('wcache: ', __version__)
            sys.exit()

        self._wcache_ip, self._wcache_port = args.ip, args.port

    @property
    def wcache_ip(self):
        return self._wcache_ip

    @property
    def wcache_port(self):
        return self._wcache_port