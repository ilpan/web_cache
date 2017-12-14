#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : commons.py
@desc    : 用于一般的socket网络通信相关的函数
@time    : 17-12-13 下午6:42 
"""


from datetime import datetime
import socket

from handler.util import get_request_info, get_host_addr
from storage import get_storage

GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'


# ===================================== 与web cache相关 ==========================================================
def do_200_response_actions(url_hash, header_lines, response_body, client_sock):
    """
    :param url_hash: 存入数据库，用来唯一确定资源
    :param header_lines: 用于获取需要存入数据库中数据，比如date和last-modified-date
    :param response_body: 存入数据库，同时封装成响应报文返回
    :param client_sock: 用于向客户端发送响应数据
    :return: 当初始服务器返回数据成功时，将response_body封装返回，同时将需要存储的数据存起来
    """

    def _get_two_date():
        """
        :return: 访问时期Date(作为saved_date)，上次修改日期Last-modified-date
        """
        saved_date = b''
        last_modified_date = b''
        header = header_lines.split(b'\r\n')
        for header_line in header:
            if header_line.startswith(b'Date'):
                _, saved_date = header_line.split(b' ', 1)
            if header_line.startswith(b'Last-Modified'):
                _, last_modified_date = header_line.split(b' ', 1)
                break
        return saved_date, last_modified_date

    # 先获得storage
    storage = get_storage()
    # 获取 Date 和 Last-Modified
    saved_date, last_modified_date = _get_two_date()

    print('saved_date: ', saved_date)           # =================================== * 输出查看 * ==
    print('last_modified: ', last_modified_date)

    mapping_data = {
        'saved_date': saved_date,
        'last_modified': last_modified_date,
        'response_body': response_body
    }
    # 首要的是先返回给客户端数据
    # TODO: 此处设计到两处不同的IO，可异步处理
    do_success_response(response_body, client_sock)
    storage.mset(url_hash, mapping_data)


def do_response(response_msg, client_sock):
    """
    :param response_msg: 响应报文
    :param client_sock: 用于向客户端发送报文
    :return: 将响应报文response_msg发给客户端
    """

    print('\r\n######## Func do_response ########')   # ========================================= * 输出查看 * ==
    print('client_sock: ', client_sock)

    # 发送响应报文
    # TODO: 后期会添加异常处理
    print('response_msg: ', response_msg)             # ========================================= * 输出查看 * ==
    client_sock.sendall(response_msg)
    client_sock.close()


def do_success_response(response_body, client_sock):
    """
    :param response_body: 响应实体
    :param client_sock: 用于向客户端发送成功报文
    :return: web cache中存在数据，封装报文直接返回
    """
    response_data = []
    status_line = 'HTTP/1.1 {} {}\r\n'.format(200, 'OK').encode('utf-8')
    header_lines = _make_response_header()
    response_data.append(status_line)
    response_data.append(header_lines)
    response_data.append(response_body)
    response_msg = b''.join(response_data)
    client_sock.sendall(response_msg)
    client_sock.close()


def _make_response_header():
    """
    :return: make header for response msg
    """
    date = datetime.utcnow().strftime(GMT_FORMAT)
    header_lines = 'Data: {}\r\nServer: WebCache\r\n\r\n'.format(date).encode('utf-8')   # 后续可根据功能再添加些首部行
    return header_lines


# ===================================== 与初始服务器有关联 =========================================================
# TODO:对于错误异常情况，可以稍后自定义一个错误报文
def get_response_msg(initial_ip, initial_port, request_msg):
    """
    :param initial_ip: 初始服务器的ip或者域名
    :param initial_port: 初始服务器的端口
    :param request_msg: 请求报文
    :return: 通过向初始服务器发送请求报文，最后获得响应报文
    """
    request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    request_socket.connect((initial_ip, initial_port))
    request_socket.sendall(request_msg)
    # 接收响应
    response_data = []
    while True:
        data = request_socket.recv(1024)
        if not data:
            break
        response_data.append(data)
    request_socket.close()      # 关闭请求连接socket
    response_msg = b''.join(response_data)

    return response_msg


def handle_other(client_sock, request_msg):
    """
    :param client_sock: 用于向客户端发会初始服务器的响应报文
    :param request_msg: 客户端的请求报文
    :return: 用于处理无需缓存响应实体的请求方法
    """
    # 1) 获得初始服务器的地址
    _, header_lines, _ = get_request_info(request_msg)
    _, ip, port = get_host_addr(header_lines)
    # 2) 获得响应报文
    response_msg = get_response_msg(ip, port, request_msg)
    # 3) 对客户端返回响应报文
    do_response(response_msg, client_sock)
