#!/usr/bin/env python
# -*- coding: utf-8 -*-

from web_cache.helper import Helper
from web_cache.server import Server

def main():
    helper = Helper()
    helper.help()
    wcache_ip, wcache_port = helper.wcache_ip, helper.wcache_port
    server = Server(wcache_ip, wcache_port)
    server.run()

if __name__ == '__main__':
    main()