#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio,logging
import aiomysql

#定义日志
def log(sql,args=()):
    logging.info('SQL:%s' % sql)


#创建连接池
async def create_pool(loop,**kw):
    logging.info('create database connection pool...')
    
    global __pool
    
    #http://aiomysql.readthedocs.io/en/latest/pool.html
    __pool=await aiomysql.create_pool(
    
        host=kw.get('host','localhost'),
        port=kw.get('port','3306'),
        user=kw.get('user'),
        password=kw.get('password'),
        db=kw.get('db'),
        
        charset=kw.get('charset','utf-8'),
        # MySQL默认操作模式就是autocommit自动提交模式。这就表示除非显式地开始一个事务，
        # 否则每个查询都被当做一个单独的事务自动执行
        # MySQL默认的存储引擎是MyISAM，MyISAM存储引擎不支持事务处理，所以改变autocommit没有什么作用。
        # 但不会报错，所以要使用事务处理的童鞋一定要确定你所操作的表示支持事务处理的，如InnoDB。
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop   
    )

#Select 
async def select(sql,args,size=None):
    log(sql,args)
    
    global __pool   
    with (await __pool) as conn:
        #http://aiomysql.readthedocs.io/en/latest/cursors.html
        #A cursor which returns results as a dictionary. All methods and arguments same as Cursor, see example:
    
        cur=await conn.cursor(aiomysql.DictCursor)
        #SQL语句的占位符是?，而MySQL的占位符是%s，select()函数在内部自动替换。
        #注意要始终坚持使用带参数的SQL，而不是自己拼接SQL字符串，这样可以防止SQL注入攻击。
        await cur.execute(sql.replace('?','%s'), args or ())
        
        #如果传入size参数，就通过fetchmany()获取最多指定数量的记录，否则，通过fetchall()获取所有记录
    
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()           
        await cur.close()
        logging.info('rows returned: %s' % len(rs))
        return rs
        
    
        
#Insert, Update, Delete
#要执行INSERT、UPDATE、DELETE语句，可以定义一个通用的execute()函数，
#因为这3种SQL的执行都需要相同的参数，以及返回一个整数表示影响的行数：

async def execute(sql,args):
    
    log(sql,args)
    
    global __pool
    with (await __pool) as conn:
        try:            
            cur=await conn.cursor()
            #execute()函数和select()函数所不同的是，cursor对象不返回结果集，而是通过rowcount返回结果数。
            await cur.execute(sql.replace('?','%s'), args or ())
            affect=cur.rowcount#受影响的条目          
            await cur.close()
        except BaseException as e:
            raise
        return affect
    

class Model():
    pass
    
    
    
    
    
    
    
    
    
    
    
    