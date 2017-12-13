#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : handle_head.py
@desc    : HEAD请求，不要求获得实体部分，故web cache只需做个转发响应就行，无需对数据存储
@time    : 17-12-12 下午8:16 
"""
from handler.commons import handle_other


def handle_head(client_sock, request_msg):

    print('\r\n######## Func handle_head ########')      # =========================================== * 输出查看 * ==

    handle_other(client_sock, request_msg)
