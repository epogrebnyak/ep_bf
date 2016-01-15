# -*- coding: utf-8 -*-
 
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, MetaData

engine = create_engine('sqlite:///:memory:', echo=True)
metadata = MetaData()

f101 = Table('f101',   metadata,
       Column('regn',  Integer, primary_key=True))

metadata.create_all(engine) 

ins = f101.insert().values(regn=0)
conn = engine.connect()
result = conn.execute(ins)
