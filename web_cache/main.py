#!/usr/bin/env python
# -*- coding: utf-8 -*-

from web_cache.server import Server

def main():
    server = Server('0.0.0.0', 6666)
    server.run()

if __name__ == '__main__':
    main()