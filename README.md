# web_cache

web_cache or wcache, is a tool that can help you store requested resources with redis

Contents
=================

  * [Installation](#installation)
  * [Usage](#usage)
  * [Architecture](#architecture)
  * [Processing flow](#processing-flow)
  * [References](#references)

## Installation
`$ pip install wcache`

## Usage
1. start server
  - default
    `$ wcache`
  - custom
    `$ wcache [--ip IP] [--port PORT]`
2. access through wcache
  - use [httpie](https://github.com/jakubroztocil/httpie) (recommend)
    eg: http --proxy http:0.0.0.0:6666 www.baidu.com
  - use browser
    just set the proxy as web_cache

## Architecture
<img src="./architecture.png" style="zoom:70%" />


## Processing flow
<img src="./process.png" style="zoom:70%" />


## References
1. <https://en.wikipedia.org/wiki/Web_cache>
2. <https://en.wikipedia.org/wiki/Proxy_server>
