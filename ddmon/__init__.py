# coding: utf-8

'''
separate dev settings and production settings
'''

from settings import *


try:
    from settings_dev import *
except:
    pass

