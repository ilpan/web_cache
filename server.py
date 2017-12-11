#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import hashlib
import socket
import threading

from handler import Handler
from storage import Storage


class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.init_storage('0.0.0.0', 6379)
        self.init_handler()
        self.init_listen_socket()
        self.init_handle_method()

    def init_storage(self, *storage_addr):
        self.storage = Storage(*storage_addr)

    def init_handler(self):
        self.handler = Handler(self.storage)

    def init_listen_socket(self):
        # 创建一个ipv4的基于tcp的监听socket，server一被关闭，port就被回收
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定ip
        self.listen_socket.bind((self.host, self.port))
        # 监听
        self.listen_socket.listen(5)

    def init_handle_method(self):
        self.handle_method = {
            b'GET': self.handler.do_get,
            b'POST': self.handler.do_post,
            b'HEAD': self.handler.do_head,
            b'DELETE': self.handler.do_delete,
            b'PUT': self.handler.do_put
        }

    # ========== end init ops =====================================================================

    # ========== start run ops =====================================================================
    def run(self):
        print('server running at {}:{} ...'.format(self.host, self.port))
        while True:
            # 等待连接
            try:
                client_socket, client_addr = self.listen_socket.accept()
                print('accept connection from {}'.format(client_addr))
                task = threading.Thread(target=self.handle_request, args=(client_socket, client_addr))
                task.start()
            except KeyboardInterrupt:
                print('\r\nServer stopped! Good Bye~')

    # ========== start handle request ==============================================================
    def handle_request(self, client_socket, client_addr):
        # 该http请求报文是encode的
        request_msg = client_socket.recv(1024)
        print('\r\n######## Func handle_request ########')  # =========================================== * 输出查看 * ==
        print('request_msg: ', request_msg)                 # =========================================== * 输出查看 * ==
        request_header, request_body = request_msg.split(b'\r\n\r\n', 1)
        request_line, header_line = request_header.split(b'\r\n', 1)
        method, url, http_version = request_line.split()
        self.handle_method[method](url, header_line, request_body, client_socket)
