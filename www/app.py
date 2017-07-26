#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

from aiohttp import web

async def index(requset):
    return web.Response(body=b'<h1>Index</h1>',content_type='text/html')
    
    
async def init(loop):
    
    app=web.Application(loop=loop);
    
    app.router.add_route('GET','/', index)
    
    #loop.create_server()则利用asyncio创建TCP服务。
    srv =await loop.create_server(app.make_handler(),'127.0.0.1',5000)
    
    return srv
    
loop=asyncio.get_event_loop()

loop.run_until_complete(init(loop))

loop.run_forever()