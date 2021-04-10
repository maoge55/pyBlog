#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Mao ZhongJie'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio

from aiohttp import web

from coroweb import get, post
from apis import APIValueError, APIResourceNotFoundError

from model import User

COOKIE_NAME = 'awesession'

@get('/{sss}')
def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    return {
        '__template__': 'index.html',
        'pid':'123',
        'cname':456
    }

@get('/')
async def test(request):
    users=await User.findAll()

    return{
        '__template__':'test.html',
        'users':users
    }