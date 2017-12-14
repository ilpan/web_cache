#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : handle_trace.py.py
@desc    : TRACE: 使服务器返回任意客户端请求的任意内容，用于远程诊断服务器
             The TRACE method echoes the received request so that a client can see what (if any) changes
            or additions have been made by intermediate servers.
@time    : 17-12-14 下午1:13 
"""
from handler.commons import handle_other


def handle_trace(client_sock, request_msg):

    print('\r\n######## Func handle_trace ########')      # =========================================== * 输出查看 * ==

    handle_other(client_sock, request_msg)
