#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : handle_connect.py
@desc    : CONNECT: 实现用隧道协议进行TCP通信，eg：SSL(安全套接字层), TLS(传输层安全)
@time    : 17-12-12 下午8:16
'''

from .commons import get_response_msg, do_response, _make_response_header
from .util import get_request_info, get_addr

def handle_connect(client_sock, request_msg):

    print('\r\n######## Func handle_connect ########')      # =========================================== * 输出查看 * ==

    request_line, request_header, _ = get_request_info(request_msg)

    _, host, _ = request_line.split(b' ')
    ip, port = get_addr(host.decode('utf-8'))

    # 向初始服务器转发，获得响应报文
    response_msg = get_response_msg(ip, port, request_msg)

    # 输出查看
    print('response_msg: ', response_msg)

    # 自定义实现一个报文，表明暂未实现该方法
    header = _make_response_header()
    body = b'<H1>Handle Connect Coming Soon......<H1>'
    response_msg = header +b'\r\n\r\n' + body
    do_response(response_msg, client_sock)