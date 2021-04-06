import asyncio, logging; logging.basicConfig(level=logging.INFO)
import aiomysql,time
from orm import __pool,select,execute,create_pool,Model,StringField,IntegerField,BooleanField
from model import User,Blog,Comment


loop= asyncio.get_event_loop()

async def test1():
    await create_pool(loop,user='www-data',password='www-data',db='awesome')
    #rss=await User.find(4)
    maoge=User(email='990835192@qq.com',passwd='123456',image='about:blank',name='junzi')
    print(time.time())
    await maoge.save()
    rss=await User.findAll()
    print(rss)

async def test2():
    await create_pool(loop,user='root',password='123456',db='test')
    sql=r'select * from user where islike=?' 
    rs=await select(sql,(False,))
    print(rs)

loop.run_until_complete(test1())
