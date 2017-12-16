#!/bin/bash

# 首先备份初始的配置文件
cur_date=`date +%Y%m%d`
mv /etc/redis/redis.conf /etc/redis/redis.conf.${cur_date}.bak
mv ./redis.conf /etc/redis/redis.conf

