#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis

class Storage:
    '''
    func: 用于web cache的存储，存储元素包括url_hash, saved_date, last_modified_date, entity_body
    '''

    def __init__(self, *address):
        self.host, self.port = address
        # 共享连接池，避免每次建立、释放连接的开销
        pool = redis.ConnectionPool(host=self.host, port=self.port)
        self.r = redis.Redis(connection_pool=pool)

    def get(self, key, field):
        return self.r.hget(key, field)

    def set(self, key, field, value):
        self.r.hset(key, field, value)

    def update(self, key, field, value):
        self.set(key, field, value)

    def mget(self, key, *field): # 可细化
        return self.r.hmget(key, *field)

    def mset(self, key, mapping):
        self.r.hmset(key, mapping)  # type of mapping为dict

    def exists(self, key):
        return self.r.exists(key)
