#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools,asyncio,logging

import os, inspect
logging.basicConfig(level=logging.INFO)
from aiohttp import web
from apier import APIError

def get(path):
    '''
    Define decorator @get('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            return func(*args,**kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator

def post(path):
    '''
    Define decorator @post('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator

    
#运用inspect模块，创建几个函数用以获取URL处理函数与request参数之间的关系
def get_required_kw_args(fn): #收集没有默认值的命名关键字参数
    args = []
    params = inspect.signature(fn).parameters #inspect模块是用来分析模块，函数
    for name, param in params.items():
        if str(param.kind) == 'KEYWORD_ONLY' and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)

def get_named_kw_args(fn):  #获取命名关键字参数
    args = []
    params = inspect.signature(fn).parameters
    for name,param in params.items():
        if str(param.kind) == 'KEYWORD_ONLY':
            args.append(name)
    return tuple(args)

def has_named_kw_arg(fn): #判断有没有命名关键字参数
    params = inspect.signature(fn).parameters
    for name,param in params.items():
        if str(param.kind) == 'KEYWORD_ONLY':
            return True

def has_var_kw_arg(fn): #判断有没有关键字参数
    params = inspect.signature(fn).parameters
    for name,param in params.items():
        if str(param.kind) == 'VAR_KEYWORD':
            return True

def has_request_arg(fn): #判断是否含有名叫'request'参数，且该参数是否为最后一个参数
    params = inspect.signature(fn).parameters
    sig = inspect.signature(fn)
    found = False
    for name,param in params.items():
        if name == 'request':
            found = True
            continue #跳出当前循环，进入下一个循环
        if found and (str(param.kind) != 'VAR_POSITIONAL' and str(param.kind) != 'KEYWORD_ONLY' and str(param.kind != 'VAR_KEYWORD')):
            raise ValueError('request parameter must be the last named parameter in function: %s%s'%(fn.__name__,str(sig)))
    return found
    
#__call__方法可以让类像函数一样调用
class RequestHandler(object):#定义RequestHandler,正式向request参数获取URL处理函数所需的参数
    def __init__(self,app,fn):
        self._app=app
        self._fn=fn
        self._required_kw_args = get_required_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._has_named_kw_arg = has_named_kw_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_request_arg = has_request_arg(fn)
        
    async def __call__(self,request):#__call__这里要构造协程
        kw = None
        if self._has_named_kw_arg or self._has_var_kw_arg:#存在关键字函数
        
            if request.method == 'POST': #判断客户端发来的方法是否为POST
                if not request.content_type: #查询有没提交数据的格式（EncType）
                    return web.HTTPBadRequest(text='Missing Content_Type.')#这里被廖大坑了，要有text
                ct = request.content_type.lower() #小写
                if ct.startswith('application/json'): #startswith
                    params = await request.json() #Read request body decoded as json.
                    if not isinstance(params,dict):
                        return web.HTTPBadRequest(text='JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    # reads POST parameters from request body.If method is not POST, PUT, PATCH, TRACE or DELETE 
                    # or content_type is not empty or application/x-www-form-urlencoded or multipart/form-data returns empty multidict.                     
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest(text='Unsupported Content_Tpye: %s'%(request.content_type))
            if request.method == 'GET': 
                qs = request.query_string #The query string in the URL
                if qs:
                    kw = dict()
                    for k,v in parse.parse_qs(qs,True).items(): 
                    #Parse a query string given as a string argument.Data are returned as a dictionary. 
                    #The dictionary keys are the unique query variable names and the values are lists of values for each name.
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._named_kw_args: #当函数参数没有关键字参数时，移去request除命名关键字参数所有的参数信息
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            for k,v in request.match_info.items(): #检查命名关键参数
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        if self._required_kw_args: #假如命名关键字参数(没有附加默认值)，request没有提供相应的数值，报错
            for name in self._required_kw_args:
                if name not in kw:
                    return web.HTTPBadRequest(text='Missing argument: %s'%(name))
        logging.info('call with args: %s' % str(kw))
        
        try:
            r = await self._fn(**kw)
            return r
        except APIError as e: #APIError另外创建
            return dict(error=e.error, data=e.data, message=e.message)
        
#注册一个URL处理函数
def add_route(app,fn):
    method = getattr(fn, '__method__', None)#post or get ex.
    path = getattr(fn, '__route__', None)# url
    
    if path is None or method is None:#未定义访问类型
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))
    
#批量注册:只需向这个函数提供要批量注册函数的文件路径，新编写的函数就会筛选，注册文件内所有符合注册条件的函数。 
#直接导入文件，批量注册一个URL处理函数
def add_routes(app,module_name):
    n = module_name.rfind('.')#Python rfind() 返回字符串最后一次出现的位置(从右向左查询)，如果没有匹配项则返回-1
    if n == -1:
        #局部名字空间可以通过内置的 locals 函数来访问。 特指当前函数或类的方法
        #全局（模块级别）名字空间可以通过 globals 函数来访问。 特指当前的模块
        mod = __import__(module_name,globals(),locals())
    else:
        name = module_name[n+1:]#取.后面的部分
        mod = getattr(__import__(module_name[:n],globals(),locals(),[name],0),name)#第一个参数为文件路径参数，不能掺夹函数名，类名
    
    # 遍历mod的方法和属性,主要是找处理方法
    # 由于我们定义的处理方法，被@get或@post修饰过，所以方法里会有'__method__'和'__route__'属性
    for attr in dir(mod):
        # 如果是以'_'开头的，一律pass，我们定义的处理方法不是以'_'开头的
        if attr.startswith('_'):
            continue
        fn = getattr(mod,attr)
        # 获取到非'_'开头的属性或方法
         # 获取有__method___和__route__属性的方法
        if callable(fn): 
            method = getattr(fn,'__method__',None) 
            path = getattr(fn,'__route__',None)
            if path and method: #这里要查询path以及method是否存在而不是等待add_route函数查询，因为那里错误就要报错了
                add_route(app,fn)
#添加静态文件夹的路径
def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'static')#输出当前文件夹中'static'的路径
    app.router.add_static('/static/',path)#prefix (str) – URL path prefix for handled static files
    logging.info('add static %s => %s'%('/static/',path))
    
    
    