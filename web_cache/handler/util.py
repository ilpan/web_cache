#!/usr/bin/env python
# -*- coding:utf-8 -*-

import gzip
import hashlib
import zlib

"""
这里存放一些与通信无关的方法
"""


# =============================== some get methods ====================================
# 解析请求报文
def get_request_info(request_msg):
    request_header, request_body = get_msg_info(request_msg)
    request_line, header_lines = request_header.split(b'\r\n', 1)
    return request_line, header_lines, request_body


# 解析响应报文
def get_response_info(response_msg):
   # print('\r\n ################## Func get_response_info #################')
    response_header, response_body = get_msg_info(response_msg)
    status_line, header_lines =  response_header.split(b'\r\n', 1)
    content_encoding = get_value_by_filed(header_lines, b'Content-Encoding')
    response_body = do_resolve_response_body(content_encoding, response_body)
    return status_line, header_lines, response_body


# 解析报文
def get_msg_info(msg):
    try:
        msg_header, msg_body = msg.split(b'\r\n\r\n', 1)
    except ValueError:
        msg_header, msg_body = msg, b''
    return msg_header, msg_body


# 获得HTTP的请求方法
def get_request_method(request_msg):
    status_line, _ = request_msg.split(b'\r\n', 1)
    request_method, _ = status_line.split(b' ', 1)
    return request_method
# =========================================== 解析整体报文结束 ==============================================


# 获取 url
def get_url(status_line):
    _, url, _ = status_line.split()
    return url


# 获得服务器返回报文实体中与field对应的value
def get_value_by_filed(header, filed):
    value = ''
    header_lines = header.split(b'\r\n')
    for header_line in header_lines:
        if header_line.startswith(filed):
            _, value = header_line.split(b' ', 1)
            break
    return value


# 用于代理向初始服务其发起请求，获得初始服务器的地址信息
def get_host_addr(header):
    host = ''
    header_lines = header.split(b'\r\n')
    for header_line in header_lines:
        h_tmp = header_line.decode('utf-8')
        if h_tmp.startswith('Host'):
            _, host = h_tmp.split()     # 该host type为str
            break
    ip, port = get_addr(host)
    return host, ip, port

def get_addr(host):
    try:
        ip, port = host.split(':')
    except ValueError:
        ip, port = host, 80
    return ip, int(port)


# ================================ some do method ====================================
# 解压缩服务器的响应实体
def do_resolve_response_body(content_encoding, response_body):
    if not content_encoding:
        return response_body
    else:
        decompress = {
            b'gzip': _do_gzip,
            b'deflate': _do_deflate
        }
        return decompress[content_encoding](response_body)


def _do_gzip(response_body):
    return gzip.decompress(response_body)


def _do_deflate(response_body):
    resolved_response_body = ''
    try:
        resolved_response_body = zlib.decompress(response_body, -zlib.MAX_WBITS)
    except zlib.error:
        resolved_response_body = zlib.decompress(response_body)
    return resolved_response_body
# ======================================== 解压缩结束 ====================================================


# ========================================= 与报文无关类 =================================================
# 获取hash值
def get_hash(url):
    sha1 = hashlib.sha1()
    sha1.update(url)
    return sha1.hexdigest()     # 该算法的结果有160bit，则共有2^160，很难重复
