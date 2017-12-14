#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : handle_get.py
@desc    : 根据请求方法，选择合适的处理器来处理
    （插一句，目前为止，经过各种测试，发现出现错误的原因是因为该web_cache未支持https，即需实现handle_connect）
@time    : 17-12-12 下午8:12
"""


from .handle_get import handle_get
from .handle_post import handle_post
from .handle_head import handle_head
from .handle_put import handle_put
from .handle_delete import handle_delete
from .handle_connect import handle_connect
from .handle_trace import handle_trace
from .handle_options import handle_options

from .util import get_request_method

GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'


class Handler:
    """
    :func: 用于处理客户端的http请求
    :处理流程:
        1) 获取到请求的URL，做hash运算到数据库中比对，若存在，执行 2)，否则执行 6)
            # 数据库中有cache
        2) 首先从数据库中获取saved_date，根据设置的保存时间与当前时间比对，没过期，则执行 3)，否则执行 4)
        3) :返: 从数据库中取出response_body，组装成响应报文，返回给客户端
        4) :发、收: 从数据库中取出last_modified，组装成请求报文，接收响应，如果存在304，则先修改expires，再执行 3)，否则执行 5)
        5) :返: 将获得的响应报文直接返回给客户端
            # 数据库中无cache
        6) :发: 将客户端的请求报文直接转发给初始服务器，接受响应，不成功则执行 5), 否则执行 7)
        7) :返: 执行 3)，先组装报文返回，后将响应数据中需要存储的存入数据库（可缓存则存）
    最佳的代理就是让客户端感觉不到代理的存在
    """

    def __init__(self):
        self.handler = {
            b'GET': handle_get,
            b'POST': handle_post,
            b'HEAD': handle_head,
            b'PUT': handle_put,
            b'DELETE': handle_delete,
            b'CONNECT': handle_connect,
            b'TRACE': handle_trace,
            b'OPTIONS': handle_options,
        }

    def handle(self, client_sock, request_msg):
        #request_msg = self.get_new_request_msg(request_msg)
        request_method = get_request_method(request_msg)
        self.handler[request_method](client_sock=client_sock, request_msg=request_msg)

    # 暂时性的，为了能够获取数据方便，使用短暂连接
    @staticmethod
    def get_new_request_msg(request_msg):
        try:
            from handler.util import get_request_info
            _, header, _ = get_request_info(request_msg)
            if b'Connection: keep-alive' in header:
                new_request_msg = request_msg.replace(b'Connection: keep-alive', b'Connection: close', 1)
            else:
                new_request_msg = request_msg
        except ValueError:
            new_request_msg = request_msg
        return new_request_msg
