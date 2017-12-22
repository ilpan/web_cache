#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading

from web_cache.handler.handler import Handler


class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.handler = Handler()
        self.init_listen_socket()

    def init_listen_socket(self):
        # 创建一个ipv4的基于tcp的监听socket，server一被关闭，port就被回收
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定ip
        try:
            self.listen_socket.bind((self.host, self.port))
        except PermissionError:
            print('Error: Permission denied')
            exit()
        except OSError:
            print('Error: Address already in use')
            exit()
        except Exception:
            print('Error: Unknown!')
            exit()
        # 监听
        self.listen_socket.listen(5)
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
                exit()

    # ========== start handle request ==============================================================
    def handle_request(self, client_sock, client_addr):
        # 该http请求报文是encode的，此处默认请求报文小于1k
        request_msg = client_sock.recv(1024)
        if not request_msg:
            return
        print('\r\n######## Func handle_request from {}########'.format(client_addr)) # ================= * 输出查看 * ==
        print('request_msg: ', request_msg)                 # =========================================== * 输出查看 * ==
        self.handler.handle(client_sock=client_sock, request_msg=request_msg)


