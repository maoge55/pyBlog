#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Mao ZhongJie'

import asyncio,aiomysql,logging;logging.basicConfig(level=logging.INFO)


__pool=None #全局变量连接池

def log(sql, args=()):
    logging.info(f'SQL:{sql}')
    
#创建连接池
async def create_pool(loop,**kw):
    global __pool
    logging.info('创建连接池...')
    __pool=await aiomysql.create_pool(
        loop=loop,
        host=kw.get('host','localhost'),
        minsize=kw.get('minsize',1),
        maxsize=kw.get('maxsize',10),
        autocommit=kw.get('autocommit',True),
        charset=kw.get('charset','utf8'),
        user=kw['user'],
        password=kw['password'],
        db=kw['db']
    )

#通用查询方法select
async def select(sql,args,size=None):
    log(sql) #控制台输出执行的sql语句
    global __pool
    async with __pool.acquire() as conn:  #异步上下文管理器async with，可以自动关闭连接
        async with conn.cursor(aiomysql.DictCursor) as cur:
            sql=sql.replace('?','%s')     #这一步的'？'其实是我们这个orm框架自己定的数据参数，你完全可以用别的合适符号代替，比如'__'
            await cur.execute(sql,args or ())
            if not size:
                rs=await cur.fetchall()
            else:
                rs=await cur.fetchmany(size)
            logging.info(f'返回行数为：{len(rs)}') #logging.info的作用跟print一样，只不过logging可以设置level参数让指定内容输出到控制台

            return rs #设置返回值可以让与select同一事件循环的协程函数里面直接通过await select()获取查询结果值,让他看起来像同步编程
    
#通用数据库增删改操作的方法
async def execute(sql,args,autocommit=True):
    log(sql)
    global __pool
    async with __pool.acquire() as conn:
        sql=sql.replace('?','%s')
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql,args)
                affected=cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected


#根据num数量生成？参数用','连接的字符串
def create_args_string(num):
    l=[]
    for n in range(num):
        l.append('?')
    
    return ','.join(l)

class Field(object):
    def __init__(self,name,column_type,primary_key,default):
        self.name=name
        self.column_type=column_type
        self.primary_key=primary_key
        self.default=default
    
    def __str__(self):
        return f'<{self.__class__.__name__}, {self.column_type}:{self.name}>'

class StringField(Field):
    def __init__(self, name=None,primary_key=False,default=None,ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

class IntegerField(Field):
    def __init__(self, name=None,  primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)

class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)

class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)

class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

class ModelMetaclass(type):
    def __new__(cls,name,bases,attrs):
        if name=='Model':
            return type.__new__(cls,name,bases,attrs)
        else:
            tableName=attrs.get('__table__',None) or name
            mappings=dict()
            fields=[]
            primaryKey=None
            for k,v in attrs.items():
                if isinstance(v,Field):
                    mappings[k]=v
                    logging.info(f'建立映射关系：{k}=>{v}')
                    if v.primary_key:
                        if primaryKey:
                            raise Exception(f'重复主键{k}')
                        primaryKey=k
                    else:
                        fields.append(k)
            
            if not primaryKey:
                raise Exception('没有声明主键')
            for k in mappings.keys():
                attrs.pop(k)
            escaped_fields=list(map(lambda f:f'`{f}`',fields))
            fieldsStr=', '.join(escaped_fields)
            upStr=', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f),fields))
            attrs['__mappings__']=mappings
            attrs['__table__']=tableName
            attrs['__primary_key__']=primaryKey
            attrs['__fields__']=fields
            attrs['__select__']=f'select `{primaryKey}`,{fieldsStr} from `{tableName}`'
            attrs['__insert__']=f'insert into `{tableName}` ({fieldsStr},`{primaryKey}`) values({create_args_string(len(escaped_fields) + 1)})'
            attrs['__update__']=f'update `{tableName}` set {upStr} where `{primaryKey}`=?'
            attrs['__delete__']=f'delete from `{tableName}` where `{primaryKey}`=?'
            return type.__new__(cls,name,bases,attrs)

class Model(dict, metaclass=ModelMetaclass):
    def __init__(self,**kw):
        super(Model, self).__init__(**kw)
        
    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'Model' object has no attribute '{key}'")

    def __setattr__(self, name, value):
        self[name]=value
    
    def getValue(self,key):
        return getattr(self, key, None)
    
    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value
    
    @classmethod
    async def findAll(cls,where=None,args=None,**kw):
        sql=[cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args=[]
        orderBy=kw.get('orderBy',None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit=kw.get('limit',None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit,int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit,tuple) and len(limit) == 2:
                sql.append('?,?')
                args.extend(limit)
            else:
                raise ValueError(f'limit错误；{limit}')
        rs=await select(' '.join(sql),args)
        return[cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls,selectFiled,where=None,args=None):
        sql=[f'select {selectFiled} _num_ from `{cls.__table__}`']
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args=()
        rss=await select(' '.join(sql),args)
        if len(rss)==0:
            return None
        return rss[0]['_num_']
    
    @classmethod
    async def find(cls,pk):
        rs=await select(f'{cls.__select__} where `{cls.__primary_key__}`=?',[pk],1)
        if(len(rs)==0):
            return None
        return cls(**rs[0])
    
    async def save(self):
        args=list(map(self.getValueOrDefault,self.__fields__)) #获取实例对象的初始化值用做参数
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows=await execute(self.__insert__,args)
        if rows !=1:
            logging.warn(f'插入数据，影响行数：{rows}')
    
    #全部更新需要输入全部字段的值
    async def update(self):
        args=list(map(self.getValue,self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows=await execute(self.__update__,args)
        if rows !=1:
            logging.warn(f'通过主键更新更新失败，影响行数：{rows}')

    #部分更新，不需要输入全部字段值
    async def updatePart(self):
        sets=''
        argss=[]
        tableN=self.__table__
        pk=self.__primary_key__
        for k,v in self.items():
            if k!=pk:
                sets+=f'`{k}`=?,'
                argss.append(v)
        sets=sets[:-1]
        argss.append(self.getValue(self.__primary_key__))
        sql=f'update `{tableN}` set {sets} where `{pk}`=?'
        rows=await execute(sql,argss)
        if rows !=1:
            logging.warn(f'通过主键更新更新失败，影响行数：{rows}')

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warn('failed to remove by primary key: affected rows: %s' % rows)
loop=asyncio.get_event_loop()




    