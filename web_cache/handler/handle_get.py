#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : handle_get.py
@desc    : GET: 用于获取资源，对于可缓存的则缓存
@time    : 17-12-12 下午8:12
"""

from datetime import datetime, timedelta

from .commons import do_response, do_success_response, do_200_response_actions
from .commons import get_response_msg
from .util import *

from web_cache.storage import get_storage


GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'


def handle_get(client_sock, request_msg):
    """
    :param client_sock: 用于向客户端发送响应
    :param request_msg: 客户端的请求报文
    :return: 在http的请求访问中，基本只有GET获取到的实体部分需要缓存，对于其他方法，无特殊要求则无需缓存（好爽）
    """

    print('\r\n######## Func handle_get ########')      # =========================================== * 输出查看 * ==

    # 获取 request_msg 中的 request_line, header_lines
    request_line, header_lines, _ = get_request_info(request_msg)
    # 获取url，作用1：用于获取url_hash; 作用二：用于组装报文
    url = get_url(request_line)
    # 获取url_hash，用于数据库比对查找数据
    url_hash = get_hash(url)

    # 获取对象初始服务器的host, ip, addr，主要用于向初始服务器发起请求
    host, ip, port = get_host_addr(header_lines)

    # 获取storage
    storage = get_storage()
    # 在web cache数据库中查找，是否存在hash表中
    if storage.exists(url_hash):
        saved_date = storage.get(url_hash, 'saved_date')
        # 过期检查
        cur_date = datetime.utcnow()
        saved_date = datetime.strptime(saved_date.decode('utf-8'), GMT_FORMAT)
        # 1) 如果还在有效期，直接返回
        if cur_date < (saved_date+timedelta(7)):
            response_body = storage.get(url_hash, 'response_body')
            print('response_body: ', response_body)
            do_success_response(response_body, client_sock)
        # 2) 若超过有效期，则使用条件GET请求
        else:
            ETag = storage.get(url_hash, 'ETag')
            last_modified_date = storage.get(url_hash, 'last_modified')
            # 此处将 ETag 和 Last-Modified合起考虑，不做单独区分了
            response_msg = do_conditional_request(url, host, ETag, last_modified_date)
            status_line, header_lines, response_body = get_request_info(response_msg)
            # 对响应做出分析
            # 若初始服务器数据未修改
            if b'304' in status_line:
                # 更新 saved_date
                new_saved_date = datetime.utcnow().strftime(GMT_FORMAT)
                storage.update(url_hash, b'saved_date', new_saved_date)
                # 直接发送给client
                response_body = storage.get(url_hash, 'response_body')
                do_success_response(response_body, client_sock)
            elif b'200' in status_line:
                print('response_body: ', response_body)
                do_200_response_actions(url_hash, header_lines, response_body, client_sock)
            else:
                do_response(response_msg, client_sock)       # 封装成响应报文发送给client

    else:
        # web cache代理发送请求并获取响应结果
        print('ip: {}, port: {}'.format(ip, port))
        response_msg = get_response_msg(ip, port, request_msg)
        print('first response_msg: ', response_msg)
        status_line, header_lines, response_body = get_response_info(response_msg)
        print('status_line: ', status_line)
        print('header_lines: ', header_lines)
        print('response_body: ', response_body)
        if b'200' in status_line:
           do_200_response_actions(url_hash, header_lines, response_body, client_sock)
        else:
            # 响应直接发给client
            do_response(response_msg, client_sock)


# ======================================= some supporting methods ==================================================
def do_conditional_request(url, host, Etag, last_modified_date):
    conditional_get_msg = _make_conditional_get_msg(url, host, Etag, last_modified_date)
    ip, port = get_addr(host)
    response_msg = get_response_msg(ip, port, conditional_get_msg)
    return response_msg


def _make_conditional_get_msg(url, host, Etag, last_modified_date):
    conditional_get_data = []
    conditional_get_request_line = 'GET {} HTTP/1.1\r\n'.format(url.decode('utf-8')).encode('utf-8')
    conditional_get_header_lines = 'Host: {}\r\nConnection: close\r\n' \
                                   'If-None_Match: {}\r\nIf-modified-since: {}\r\n\r\n'.\
                                    format(host, Etag, last_modified_date.decode('utf-8')).encode('utf-8')
    conditional_get_data.append(conditional_get_request_line)
    conditional_get_data.append(conditional_get_header_lines)
    proxy_conditional_get_request = b''.join(conditional_get_data)
    return proxy_conditional_get_request
