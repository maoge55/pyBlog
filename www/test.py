import asyncio, logging; logging.basicConfig(level=logging.INFO)
import aiomysql,time,inspect
from orm import __pool,select,execute,create_pool,Model,StringField,IntegerField,BooleanField
loop= asyncio.get_event_loop()

import requests,json
#r = requests.get('http://localhost:9000', params={'q': 'python', 'cat': '1001'})
data={'form_email': 'abc@example.com', 'form_password': '123456'}
data_json = json.dumps(data)
r = requests.post('http://localhost:9000/maoge/abc',json=data)
print(r.content)


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

#loop.run_until_complete(test1())



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


