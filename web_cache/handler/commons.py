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

from .util import get_request_info, get_host_addr, get_request_method, get_value_by_filed
from web_cache.storage import get_storage

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
    # 获得ETag
    ETag = get_value_by_filed(header_lines, b'ETag')

    print('saved_date: ', saved_date)           # =================================== * 输出查看 * ==
    print('last_modified: ', last_modified_date)
    print('ETag: ', ETag)

    mapping_data = {
        'saved_date': saved_date,
        'ETag': ETag,
        'last_modified': last_modified_date,
        'response_body': response_body
    }
    # 首要的是先返回给客户端数据
    # TODO: 此处设计到两处不同的IO，可异步处理
    do_success_response(response_body, client_sock)

    cache_control = get_value_by_filed(header_lines, b'Cache-Control')
    if b'no-store' in cache_control:
        # 不执行下一步缓存操作
        return

    if saved_date and ETag and last_modified_date and response_body:
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
    print('request_msg in func get_response_msg: ', request_msg)
    request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    request_socket.connect((initial_ip, initial_port))
    request_method = get_request_method(request_msg)
    head_request_msg = request_msg.replace(request_method, b'HEAD', 1)
    print('head_request_msg: ', head_request_msg)
    request_socket.sendall(head_request_msg)

    # 此处默认头部信息小于8k
    header_res = request_socket.recv(8192)
    print('header_res: ', header_res)

    # 发送正式的请求报文
    request_socket.sendall(request_msg)
    # 接收响应
    response_data = []

    '''
    ### 经过测试发现，当使用head请求时若报文中既无C-L又无T-E，则使用get时报文中会有T-E
    ### 所以对于GET报文中C-L和T-E两者必存在一个，不会同时存在或者同时不存在
    ### 注意到，该方法对于handle_other也有调用，即对于其他报文，可能以上两者都无
    if b'Content-Length' not in header_res:
        if b'Transfer-Encoding' not in header_res:
            print('=============Process Here: not wished===============')
            header_length = len(header_res)
            data =  request_socket.recv(header_length)
            response_data.append(data)
            print('Not Wished Response_data: ', data)
    '''

    if b'Content-Length' in header_res:
        header_length = len(header_res)
        print('\r\nheader_length: ', header_length)
        content_length = int(get_value_by_filed(header_res, b'Content-Length'))
        # 1）接收header
        header = request_socket.recv(header_length)     # 此处默认成功的返回请求的header大小一样
        response_data.append(header)
        print('\r\nheader: ', header)
        # 2) 接受实体部分
        recv_content_length = 0
        recv_size = 1024 if content_length < 8192 else 8192
        while recv_content_length < content_length:
            data = request_socket.recv(recv_size)
            print('CL-Data: ', data)
            response_data.append(data)
            recv_content_length += 1024
        # ================ 输出查看 ================
        print('content_length: ', content_length)
        print('recv_content_length: ', recv_content_length)
    else:
        # 数据采用分块传输, 目前为止应该就'chunked'一种传输编码
        # 每个chunk分为头部和正文，对应于最后一个chunk其头部为0，正文为空
        while True:
            data = request_socket.recv(8192)
            #if not data:
            #    break       # 不是T-E也不是C-L，“不明情况”
            print('TE-Data: ', data)
            response_data.append(data)
            if data.endswith(b'\r\n0\r\n\r\n'):
                break

    # 关闭请求连接socket
    request_socket.close()

    response_msg = b''.join(response_data)
    print('response_msg: ', response_msg)

    # 重新组装response_msg
    if b'Transfer-Encoding' in response_msg:
        response_header, response_body = response_msg.split(b'\r\n\r\n' ,1)
        res_body_list = response_body.split(b'\r\n')
        print('response_body in T-E1: ', response_body)
        print('res_body_list in T-E: ', res_body_list)
        res_body_data = []
        body_len = len(res_body_list)
        print('body_len in T-E: ', body_len)
        for i in range(0, body_len, 2):
            chunk = res_body_list[i+1]
            if int(res_body_list[i], 16) == 0:
           # if not chunk:
                break
            res_body_data.append(chunk)
        response_body = b''.join(res_body_data)
        print('response_body in T-E2: ', response_body)
        response_msg = response_header + b'\r\n\r\n' + response_body

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
