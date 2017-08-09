#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re, time, json, logging, hashlib, base64, asyncio

#import markdown2

from aiohttp import web

from clweb import get, post
from apier import APIValueError,APIResourceNotfoundError


@get('/')
async def index(request):
    #return web.Response(body=b'<h1>Index</h1>',content_type='text/html')
    body=b'<h1>Index</h1>'
    return body
 
@get('/greeting')
async def handler_url_greeting(*,name,request):
    body='<h1>Awesome: /greeting %s</h1>'%name
    return body 