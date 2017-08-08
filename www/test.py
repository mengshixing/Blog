#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio,logging
import aiomysql
import orm,model
import sys
# import time, uuid

# print (uuid.uuid4())
# print (uuid.uuid4().hex)
# print (int(time.time() * 1000), uuid.uuid4().hex)
#'%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

# async def test_save():
    # user = User(id="123", name="Caisw")
    # await user.save()
# async def test_find():
    # user = await User.find("123")
    # print(user)

# print ('%015d' % int(time.time() * 10000000000))
# loop=asyncio.get_event_loop()
# loop.run_until_complete(orm.create_pool(loop=loop,user='root',password='root',db='blog'))
# loop.run_until_complete(orm.execute('select * from users',()))
#loop.run_until_complete(asyncio.wait([orm.create_pool(loop=loop,user='root',password='root',db='blog'),orm.execute('select * from users',())]))
#__pool.close()
#loop.run_until_complete(__pool.wait_closed())
#loop.close()

# class A:   
    # def __init__(self):   
        # self.a = 'a'  
    # def method(self):   
        # print ("method print")    
# a = A()   
# print(getattr(a, 'a', 'default')) #如果有属性a则打印a，否则打印default   
# print (getattr(a, 'b', 'default')) #如果有属性b则打印b，否则打印default   
# print (getattr(a, 'method', 'default'))#如果有方法method，否则打印其地址，否则打印default   
# print (getattr(a, 'method', 'default')())#如果有方法method，运行函数并打印None否则打印default 

#测试查询

async def tt(): 
    #r=await model.User.find('1') 查
    #r=await model.User(id=123, name='Michael',passwd='222',image='2.jpg',email='2@1.com').save() 增
    #r=await model.User(id=123, name='Michael',passwd='222',image='2.jpg',email='3333@1222.com').update()
    r=await model.User(id=123).remove()
    #print(r)
    
loop=asyncio.get_event_loop()
loop.run_until_complete(orm.create_pool(loop=loop,user='root',password='root',db='blog'))
loop.run_until_complete(tt())

#print(user)
#loop.run_until_complete(await User.find('1'))

loop.close()
#sys.exit()#处理RuntimeError: Event loop is closed


