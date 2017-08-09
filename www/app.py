#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging

logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web
from jinja2 import Environment, FileSystemLoader

import orm
from clweb import add_routes, add_static,get,post
from aiohttp import web

#初始化jinja2，以便其他函数使用jinja2模板
def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape = kw.get('autoescape', True),
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        variable_start_string = kw.get('variable_start_string', '{{'),
        variable_end_string = kw.get('variable_end_string', '}}'),
        auto_reload = kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env
    
async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))#ex:Request: GET /
        logging.info(handler)
        # await asyncio.sleep(0.3)
        return (await handler(request))
    return logger 
 
# 暂时不用 
async def data_factory(app, handler):
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.info('request json: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                logging.info('request form: %s' % str(request.__data__))
        return (await handler(request))
    return parse_data

# 暂时不用
# 通过cookie找到当前用户信息，把用户绑定在request.__user__ 
async def auth_factory(app, handler):
    async def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        cookie = request.cookies.get(COOKIE_NAME)
        request.__user__ = await User.find_by_cookie(cookie)
        if request.__user__ is not None:
            logging.info('set current user: %s' % request.__user__.email)
        return await handler(request)
    return auth
    
async def response_factory(app, handler):#函数返回值转化为`web.response`对象
    async def response(request):
        logging.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            #r.content_type = 'text/plain;charset=utf-8'
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            #resp.content_type = 'application/octet-stream'
            resp.content_type = 'text/plain;charset=utf-8'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):#重定向
                return web.HTTPFound(r[9:])#转入别的网站
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None: 
                #序列化JSON那章，传递数据https://docs.python.org/2/library/json.html#basic-usage
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:#jinja2模板
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r >= 100 and r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(t, str(m))
        # default: # default，错误
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response
    
def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


    
async def init(loop):
    await orm.create_pool(loop=loop,user='root',password='root',db='blog')
    #await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='www', password='www', db='awesome')
    app=web.Application(loop=loop,middlewares=[logger_factory,response_factory]);
    
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    add_routes(app, 'handlers')
    add_static(app)
    
    
    #app.router.add_route('GET','/', index)
    
    #loop.create_server()则利用asyncio创建TCP服务。
    srv =await loop.create_server(app.make_handler(),'127.0.0.1',5000)
    
    logging.info('server started at http://127.0.0.1:5000...')
    return srv
    
loop=asyncio.get_event_loop()

loop.run_until_complete(init(loop))

loop.run_forever()