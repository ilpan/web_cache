#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : handle_options.py
@desc    : OPTIONS: 询问可以执行哪些方法
            The OPTIONS method returns the HTTP methods that the server supports for the specified URL.
            This can be used to check the functionality of a web server by requesting '*' instead of a specific resource.
@time    : 17-12-14 下午1:14 
"""
from .commons import handle_other


def handle_options(client_sock, request_msg):

    print('\r\n######## Func handle_trace ########')      # =========================================== * 输出查看 * ==

    handle_other(client_sock, request_msg)
