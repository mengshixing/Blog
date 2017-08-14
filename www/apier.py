#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, logging, inspect, functools

class Page(object):
    '''
    Page object for display pages.
    '''
    #总条数,页码,每页条数
    def __init__(self, item_count, page_index=1, page_size=10):
        '''
        Init Pagination by item_count, page_index and page_size.
        >>> p1 = Page(100, 1)
        >>> p1.page_count
        10
        >>> p1.offset
        0
        >>> p1.limit
        10
        >>> p2 = Page(90, 9, 10)
        >>> p2.page_count
        9
        >>> p2.offset
        80
        >>> p2.limit
        10
        >>> p3 = Page(91, 10, 10)
        >>> p3.page_count
        10
        >>> p3.offset
        90
        >>> p3.limit
        10
        '''
        self.item_count = item_count
        self.page_size = page_size
        #//浮点数除法,结果四舍五入,计算出总页数
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0)
        #总条数为0或者页码大于总页数
        #limit后面跟的是n条数据，offset后面是从第n条开始读取
        if (item_count == 0) or (page_index > self.page_count):
            self.offset = 0
            self.limit = 0
            self.page_index = 1
        else:
            self.page_index = page_index
            self.offset = self.page_size * (page_index - 1)
            self.limit = self.page_size
        #判断是否存在上一页,下一页
        self.has_next = self.page_index < self.page_count
        self.has_previous = self.page_index > 1

    def __str__(self):
        return 'item_count: %s, page_count: %s, page_index: %s, page_size: %s, offset: %s, limit: %s' % (self.item_count, self.page_count, self.page_index, self.page_size, self.offset, self.limit)

    __repr__ = __str__

class APIError(Exception):
    '''
    基础的APIError，包含错误类型(必要)，数据(可选)，信息(可选)
    '''
    def __init__(self,error,data = '',message = ''):
        super(APIError,self).__init__(message)
        self.error = error
        self.data = data
        self.message = message

class APIValueError(APIError):
    '''
    Indicate the input value has error or invalid. The data specifies the error field of input form.
    表明输入数据有问题，data说明输入的错误字段
    '''
    def __init__(self,field,message = ''):
        super(APIValueError,self).__init__('Value: invalid',field,message)

class APIResourceNotfoundError(APIError):
    '''
    Indicate the resource was not found. The data specifies the resource name.
    表明找不到资源，data说明资源名字
    '''
    def __init__(self,field,message = ''):
        super(APIResourceNotFoundError,self).__init__('Value: Notfound',field,message)

class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    接口没有权限
    '''
    def __init__(self,message = ''):
        super(APIPermissionError,self).__init__('Permission: forbidden','Permission',message)