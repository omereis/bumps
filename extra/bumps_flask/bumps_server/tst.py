#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import asyncio
import websockets
from multiprocessing import Process, Pipe
import functools
from sqlalchemy import create_engine, MetaData
from bumps_constants import *


database_engine = create_engine('mysql+pymysql://bumps:bumps_dba@NCNR-R9nano.campus.nist.gov:3306/bumps_db')
connection = database_engine.connect()
job_id = 358
strSql = f'select {DB_Field_ResultsDir} from {DB_Table} where {DB_Field_JobID}={job_id};'
try:
    res = connection.execute(strSql)
    for row in res:
        print(f'{row[0]}')
except Exception as e:
    print(f'Error {e}')
finally:
    connection.close()
exit(0)

async def hello(websocket, path, parent_conn):
    name = await websocket.recv()
    print(f'got parent conn')
    parent_conn.send(name)
   
def f(conn):
    while True:
        if conn.poll():
            stuff = conn.recv()
            print("Stuff in fconn is: {}".format(stuff))
            
if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=f, args=(child_conn,))
    p.start()
    try:
        start_server = websockets.serve(functools.partial(hello, parent_conn=parent_conn), 'localhost', 5555)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print(f'Error: "{e}"')
exit(0)

class Job:
    id = None
    def __init__ (self, num):
        self.id = num

IDs = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
listJobs = []
for id in IDs:
    listJobs.append(Job(id))

for n in range(len(listJobs)):
    print(f'index {n}, id: {listJobs[n].id}')

delIdx = ['5', '10']

n = 0
while n < len(listJobs):
    if str(listJobs[n].id) in delIdx:
        listJobs.pop(n)
    else:
        n += 1

print('\nafter deleting')
for n in range(len(listJobs)):
    print(f'index {n}, id: {listJobs[n].id}')
