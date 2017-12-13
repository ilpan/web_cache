#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : handle_post.py
@desc    : POST: 数据格式、大小无限制，主要目标是传输实体文本，并非获取响应的实体部分，故暂无需考虑将响应实体缓存
@time    : 17-12-12 下午8:15 
"""
from handler.commons import handle_other


def handle_post(client_sock, request_msg):

    print('\r\n######## Func handle_post ########')      # =========================================== * 输出查看 * ==

    # 只需将POST报文转发给初始服务器，使得初始服务器发生改变即可
    handle_other(client_sock, request_msg)
