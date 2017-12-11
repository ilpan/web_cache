#!/usr/bin/env python

from datetime import datetime, timedelta
import socket

from util import *


GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'


class Handler:

    def __init__(self, storage):
        self.storage = storage

    def do_get(self, *args):
        status_code = '404'         # 默认为404
        url, header_line, _, client_sock = args
        url_hash = get_hash(url)

        # 首先获取对象初始服务器的host, ip, addr
        host, ip, port = get_host_addr(header_line)

        # 在web cache数据库中查找，是否存在hash表中
        if self.storage.exists(url_hash):
            saved_date, last_modified_date, response_body = \
                self.storage.mget(url_hash, b'saved_date', b'last_modified_date', b'entity_body')
            # 过期检查，有效时间设为一周
            cur_date = datetime.utcnow()
            saved_date = datetime.strptime(saved_date.decode('utf-8'), GMT_FORMAT)
            # 1) 如果还在有效期，直接返回
            if cur_date < (saved_date + timedelta(7)):
                status_code = '200'
                self.do_get_response(response_body, status_code, client_sock)       # 封装成响应报文发送给client
            # 2) 若超过有效期，则使用条件GET请求
            else:
                proxy_conditional_request = self._get_proxy_conditional_get_msg(url, host, last_modified_date)
                # 发送该请求并获得响应结果
                status_line, header_line, response_body = \
                    self._get_response_msg(ip, port, proxy_conditional_request)

                # 对响应做出分析
                # 若初始服务器数据未修改
                if b'304' in status_line:
                    # 更新saved_date
                    new_saved_date = datetime.utcnow().strftime(GMT_FORMAT)
                    self.storage.update(url_hash, b'saved_date', new_saved_date)
                    # 直接发送给client
                    status_code = '200'
                    self.do_get_response(response_body, status_code, client_sock)       # 封装成响应报文发送给client
                else:
                    # 此处默认初始服务器该数据存在，只不过数据被修改了
                    # 获取 Date 和 Last-Modified
                    saved_date, last_modified_date = self._get_two_date(header_line)
                    mapping_data = {
                        'saved_date': saved_date,
                        'last_modified_date': last_modified_date,
                        'entity_body': response_body
                    }
                    if b'200' in status_line:
                        self.storage.mset(url_hash, mapping_data)

                    _, status_code, _ = status_line.split(b' ', 2)
                    status_code = status_code.decode('utf-8')
                    self.do_get_response(response_body, status_code, client_sock)

        else:
            # 1) 获得被请求主机的地址
            # 2) 连接被请求的主机
            # 3) 封装请求报文（可控性）
            print('\r\n######## Func do_get ########')      # =========================================== * 输出查看 * ==
            proxy_request = self._get_proxy_normal_get_msg(url, host)
            print('proxy_request: ', proxy_request)         # =========================================== * 输出查看 * ==
            # 4) web cache代理发送请求并获取响应结果
            status_line, header_line, response_body = self._get_response_msg(ip, port, proxy_request)
            # 获取 Date 和 Last-Modified
            saved_date, last_modified_date = self._get_two_date(header_line)
            mapping_data = {
                'saved_date': saved_date,
                'last_modified_date': last_modified_date,
                'entity_body': response_body
            }
            if b'200' in status_line:
                self.storage.mset(url_hash, mapping_data)

            # 7) 处理响应，发给client
            _, status_code, _ = status_line.split(b' ', 2)
            status_code = status_code.decode('utf-8')
            self.do_get_response(response_body, status_code, client_sock)


    def do_get_response(self, *args):
        status_msg = {
            '200': 'OK',
            '301': 'Moved Permanently',
            '302': 'Temporarily Moved',
            '304': 'Not Modified',
            '400': 'Bad Request',
            '404': 'Not Found',
            '505': 'HTTP Version Not Support'
        }

        response_body, status_code, client_sock = args

        print('\r\n######## Func do_get_response ########')   # ========================================= * 输出查看 * ==
        print('client_sock: ', client_sock)

        # 封装响应报文
        proxy_response = self._get_proxy_response_msg(status_code, status_msg[status_code], response_body)
        # 发送响应报文
        # TODO: 后期会添加异常处理
        print('proxy_response: ', proxy_response)             # ========================================= * 输出查看 * ==
        client_sock.sendall(proxy_response)
        client_sock.close()

    def do_post(self):
        pass

    def do_head(self):
        pass

    def do_delete(self):
        pass

    def do_put(self):
        pass

    # ======================================= some supporting methods ==================================================
    def _get_response_msg(self, initial_ip, initial_port, request_msg):
        conditional_request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conditional_request_socket.connect((initial_ip, initial_port))
        conditional_request_socket.sendall(request_msg)
        # 接收响应
        response_buf = []
        while True:
            data = conditional_request_socket.recv(1024)
            if not data:
                break
            response_buf.append(data)
        conditional_request_socket.close()      # 关闭请求连接socket
        response_msg = b''.join(response_buf)
        response_header, response_body = response_msg.split(b'\r\n\r\n', 1)
        status_line, header_line = response_header.split(b'\r\n', 1)
        return status_line, header_line, response_body

    def _get_two_date(self, header_line):
        '''
        :return: 访问时期Date(作为saved_date)，上次修改日期Last-modified-date
        '''
        saved_date = b''
        last_modified_date = b''
        header_lines = header_line.split(b'\r\n')
        for header in header_lines:
            if header.startswith(b'Date'):
                _, saved_date = header.split(b' ', 1)
            if header.startswith(b'Last-Modified'):
                _, last_modified_date = header.split(b' ', 1)
                break
        return saved_date, last_modified_date

    def _get_proxy_normal_get_msg(self, url, host):
        request_buf = []
        request_line = 'GET {} HTTP/1.1\r\n'.format(url.decode('utf-8')).encode('utf-8')
        request_header_line = 'Host: {}\r\nConnection: close\r\n\r\n'.format(host).encode('utf-8')
        request_buf.append(request_line)
        request_buf.append(request_header_line)
        proxy_request = b''.join(request_buf)
        return proxy_request

    def _get_proxy_conditional_get_msg(self, url, host, last_modified_date):
        conditional_buf = []
        conditional_request_line = 'GET {} HTTP/1.1\r\n'.format(url.decode('utf-8')).encode('utf-8')
        conditional_header_line = 'Host: {}\r\nConnection: close\r\n' \
                'If-modified-since: {}\r\n\r\n'.format(host, last_modified_date.decode('utf-8')).encode('utf-8')
        conditional_buf.append(conditional_request_line)
        conditional_buf.append(conditional_header_line)
        proxy_conditional_request = b''.join(conditional_buf)
        return proxy_conditional_request

    def _get_proxy_response_msg(self, status_code, status_description, response_body):
        response_buf = []
        status_line = 'HTTP/1.1 {} {}\r\n'.format(status_code, status_description).encode('utf-8')
        date = datetime.utcnow().strftime(GMT_FORMAT)
        header_line = 'Data: {}\r\nServer: WebCache\r\n\r\n'.format(date).encode('utf-8')   # 后续可根据功能再添加些首部行
        response_buf.append(status_line)
        response_buf.append(header_line)
        response_buf.append(response_body)
        proxy_response = b''.join(response_buf)
        return proxy_response