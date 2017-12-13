#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : handle_delete.py
@desc    : DELETE: 从服务器中删除URI指定的资源
@time    : 17-12-12 下午8:16 
"""
from handler.commons import handle_other


def handle_delete(client_sock, request_msg):

    print('\r\n######## Func handle_delete ########')      # =========================================== * 输出查看 * ==

    handle_other(client_sock, request_msg)
