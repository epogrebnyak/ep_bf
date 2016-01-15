# -*- coding: utf-8 -*-
 
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Date, MetaData

engine = create_engine('sqlite:///:memory:', echo=True)
#engine = create_engine('sqlite:///122012.sqlite3', echo=True)


metadata = MetaData()
f101 = Table('f101',   metadata,
       Column('regn',  Integer, primary_key=True),
       Column('plan',  String),
       Column('conto', Integer, primary_key=True),
       Column('a_p',   Integer),
       Column('ir',    Integer),
       Column('iv',    Integer),
       Column('itogo', Integer, primary_key=True),
       Column('dt',    Date,    primary_key=True)
       )

metadata.create_all(engine)        
       
from dbf_stream import  yield_dicts             
gen = yield_dicts('122012')
conn = engine.connect()
conn.execute(f101.delete())
conn.execute(f101.insert(), [x for x in gen])

#REPLACE [LOW_PRIORITY | DELAYED]
#    [INTO] tbl_name [(col_name,...)]
#    {VALUES | VALUE} ({expr | DEFAULT},...),(...),...