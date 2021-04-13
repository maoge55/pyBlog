import asyncio, logging; logging.basicConfig(level=logging.INFO)
import aiomysql,time,inspect
from orm import __pool,select,execute,create_pool,Model,StringField,IntegerField,BooleanField
from model import User
loop= asyncio.get_event_loop()

import requests,json,hashlib
#r = requests.get('http://localhost:9000/api/users', params={'q': 'python', 'cat': '1001'})
# data={'form_email': 'abc@example.com', 'form_password': '123456'}
# data_json = json.dumps(data)
# r = requests.post('http://localhost:9000/maoge/abc',json=data)
# ooo=r.json()
# print(ooo)
# print(type(ooo))


async def test1():
    await create_pool(loop,user='www-data',password='www-data',db='awesome')
    #rss=await User.find(4)
    rss=(await User.findAll('name=?',['maoge']))[0]
    print(rss)
    rss.image=f'http://www.gravatar.com/avatar/{hashlib.md5(rss.email.encode("utf-8")).hexdigest()}?d=mm&s=120'
    print(rss)
    await rss.update()

async def test2():
    await create_pool(loop,user='root',password='123456',db='test')
    sql=r'select * from user where islike=?' 
    rs=await select(sql,(False,))
    print(rs)

loop.run_until_complete(test1())



def get_required_kw_args(fn):
    args=[]
    params=inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind==inspect.Parameter.KEYWORD_ONLY and param.default==inspect.Parameter.empty:
            args.append(name)

    return tuple(args)

def get_named_kw_args(fn):
    args=[]
    params=inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind==inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    
    return tuple(args)

def maoge(a,b,*c,ol,jk,pp,pid=123,name='maoge',**kw):
    pass


