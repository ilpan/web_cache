#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib


# 获取url的hash值
def get_hash(url):
    sha1 = hashlib.sha1()
    sha1.update(url)
    return sha1.hexdigest()     # 该算法的结果有160bit，则共有2^160，很难重复


def get_host_addr(header_line):
    host = ''
    header = header_line.split(b'\r\n')
    for h in header:
        h_tmp = h.decode('utf-8')
        if h_tmp.startswith('Host'):
            _, host = h_tmp.split()     # 该host type为str
            break
    try:
        ip, port = host.split(':')
    except:
        ip, port = host, 80

    return host, ip, int(port)