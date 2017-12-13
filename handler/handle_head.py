#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : handle_head.py
@desc    : HEAD请求，不要求获得实体部分，故web cache只需做个转发响应就行，无需对数据存储
@time    : 17-12-12 下午8:16 
"""
from handler.commons import get_response_msg, do_response
from handler.util import get_request_info, get_host_addr, get_msg_info


def handle_head(client_sock, request_msg):

    print('\r\n######## Func handle_head ########')      # =========================================== * 输出查看 * ==

    request_line, header_lines, _ = get_request_info(request_msg)

    host, ip, port = get_host_addr(header_lines)

    response_msg = get_response_msg(ip, port, request_msg)

    do_response(response_msg, client_sock)

