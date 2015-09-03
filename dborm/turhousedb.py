# -*- coding: utf-8 -*-


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from glob import Glob
from ormbase import OrmBase

from drivers import genericdevice
from alarm import alarmzone

'''
    module implementing turhouse db connection
'''


def dbConnect():
    '''
        Create an engine
    '''
    Glob.dbEngine = create_engine(Glob.config.db())
    OrmBase.metadata.create_all(Glob.dbEngine, checkfirst=True)
    Glob.dbSession = sessionmaker(bind=Glob.dbEngine, expire_on_commit=False)


def get_or_create(session, model, **kwargs):
    '''
        Creates an object or returns the object if exists
        from: http://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create
    '''
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance
