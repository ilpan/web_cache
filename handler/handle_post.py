#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : handle_post.py
@desc    :      
@time    : 17-12-12 下午8:15 
"""
from handler.commons import get_response_msg
from handler.util import get_host_addr, get_request_info


def handle_post(client_sock, request_msg):

    print('\r\n######## Func handle_post ########')      # =========================================== * 输出查看 * ==

