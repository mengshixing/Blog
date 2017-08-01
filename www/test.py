#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#import asyncio,logging
#import aiomysql

import orm
import time, uuid

print (uuid.uuid4())
print (uuid.uuid4().hex)
print (int(time.time() * 1000), uuid.uuid4().hex)
#'%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

print ('%015d' % int(time.time() * 10000000000))

loop=asyncio.get_event_loop()

loop.run_until_complete()

loop.close()