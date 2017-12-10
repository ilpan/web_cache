#!/usr/bin/env python

from server import Server

def main():
    server = Server('0.0.0.0', 6666)
    server.run()

if __name__ == '__main__':
    main()
