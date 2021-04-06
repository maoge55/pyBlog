import asyncio, logging; logging.basicConfig(level=logging.INFO)
import aiomysql
from orm import __pool,select,execute,create_pool,loop,Model,StringFiled,IntegerField,BooleanField


class User(Model):
    __table__ = 'user'
    uid=IntegerField(name='uid',primary_key=True)
    uname=StringFiled('uname')
    islike=BooleanField('islike')


async def test1():
    await create_pool(loop,user='root',password='123456',db='test')
    #rss=await User.find(4)
    rss=await User.findAll()
    print(rss)

async def test2():
    await create_pool(loop,user='root',password='123456',db='test')
    sql=r'select * from user where islike=?' 
    rs=await select(sql,(False,))
    print(rs)



#loop.run_until_complete(test1())
