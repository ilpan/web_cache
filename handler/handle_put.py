#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : handle_put.py
@desc    : PUT: 用于传输文件，类似FTP，但存在安全问题，为了项目完整性，包含该方法
@time    : 17-12-12 下午8:16 
"""
from handler.commons import handle_other


def handle_put(client_sock, request_msg):

    print('\r\n######## Func handle_put ########')      # =========================================== * 输出查看 * ==

    handle_other(client_sock, request_msg)