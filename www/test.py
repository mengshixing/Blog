#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio,logging
import aiomysql

import orm
import time, uuid

print (uuid.uuid4())
print (uuid.uuid4().hex)
print (int(time.time() * 1000), uuid.uuid4().hex)
#'%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

# async def test_save():
    # user = User(id="123", name="Caisw")
    # await user.save()


# async def test_find():
    # user = await User.find("123")
    # print(user)


print ('%015d' % int(time.time() * 10000000000))

loop=asyncio.get_event_loop()

loop.run_until_complete(orm.create_pool(loop=loop,user='root',password='root',db='blog'))

loop.run_until_complete(orm.execute('select * from users',()))

#loop.run_until_complete(asyncio.wait([orm.create_pool(loop=loop,user='root',password='root',db='blog'),orm.execute('select * from users',())]))
#__pool.close()
#loop.run_until_complete(__pool.wait_closed())
loop.close()
