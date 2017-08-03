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
    
        host=kw.get('host','127.0.0.1'),
        #端口号不能输入字符串.self.host_info = "socket %s:%d" % (self._host, self._port)
        #TypeError: %d format: a number is required, not str
        port=kw.get('port',3306),
        user=kw.get('user'),
        password=kw.get('password'),
        db=kw.get('db'),
        
        #此处utf8不能写成utf-8否则'Connection' object has no attribute '_writer'        
        charset=kw.get('charset','utf8'),
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
        #执行完SQL语句,释放与数据库的连接。    
        finally:
            conn.close()
        #print(affect)
        return affect
    
# 定义字段基类
# 在我们编写一个新的Python类的时候，总是在最开始位置写一个初始化方法__init__，
# 以便初始化对象，然后会写一个__str__方法，方面我们调试程序。
class Field(object):
    def __init__(self,name,column_type,primary_key,default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default
        
    def __str__(self):
        return '<%s,%s:%s>' % (self.__class__.__name__,self.column_type,self.name)
        
class StringField(Field):
    def __init__(self,name=None,primary_key=False,default=None,ddl='varchar(100)'):
        super().__init__(name,ddl,primary_key,default)
        
class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)

class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)

class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)   
    
# id = StringField(primary_key=True, default='2222', ddl='varchar(50)')
# if __name__=='__main__':
    # print(id);  输出<StringField,varchar(50):None>
    
    
#通过metaclass：ModelMetaclass：将具体的子类如User的映射信息读出
# >>> type(type)  <class 'type'> ，`type`是一个元类`metaclass`
#metaclass 元类,控制类的创建行为,类可以看成是元类创建的实例,动态修改类
class ModelMetaclass(type):
    def __new__(cls,name,bases,attrs):
        if name='Model':#排除Model类
            return type.__new__(cls,name,bases,attrs)
        
        tableName=attrs.get('__table__',None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        
        # 获取所有的Field和主键名:
		mappings=dict()
		fields=[]
		primaryKey=None
		for k,v in attrs.items():#查找Field属性放入字典
            if isinstance(v,Field):
				mappings[k]=v
                logging.info('found mapping: %s ==> %s' % (k, v))
				if v.primary_key:#如果是主键
					if primaryKey:
						#主键重复了
						raise RuntimeError('Duplicate primary key for field: %s' % k)
					primaryKey = k
				else:					 
					fields.append(k)
		if not primaryKey:
			#遍历完之后发现没有主键
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():#从类属性中删除Field属性
            attrs.pop(k)    
		#把不含主键的段组成字符串数组	
		escaped_fields=list(map(lambda f:"'%s'" % f,fields))
        attrs['__mappings__']=mappings #保存属性和列的映射关系
        attrs['__table__']=tableName #表名简化为类名
		attrs['__primary_key__'] = primaryKey # 主键属性名
        attrs['__fields__'] = fields # 除主键外的属性名集合
		
		# 构造默认的SELECT, INSERT, UPDATE和DELETE语句:
        attrs['__select__'] = 'select `%s‘, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
		
		
        return type.__new__(cls,name,bases,attrs)
		
		
		
		
            
        
class Model():
    pass
    
    
    
    
    
    
    
    
    
    
    
    