# coding: utf-8

import sqlite3
import os
import json
print os.getcwd()

conn = sqlite3.connect('data/vm_flaw.db')
c = conn.cursor()
# c.execute('CREATE TABLE FLAW_TABLE(ID INT NOT NULL, DEPT CHAR(50) NOT NULL)')
# c.execute('INSERT INTO FLAW_TABLE(ID, DEPT) VALUES(1, "Norway")')

try:
    c.execute('CREATE TABLE FLAW_TABLE('
              'CNVD_ID VARCHAR(20),'
              'TIME VARCHAR(12),'
              'DENLE VARCHAR(10),'
              'IMPACT_PRODUCT varchar(30),'
              'TITLE VARCHAR(255),'
              'DETAIL VARCHAR(255))')
except:
    print 'exists. . .'
flaw_file = open('data/data.txt', 'r')

insert_sql = 'INSERT INTO FLAW_TABLE(CNVD_ID, TIME, DENLE, IMPACT_PRODUCT, TITLE, DETAIL)' \
             'VALUES ("%s", "%s", "%s", "%s", "%s",  "%s")'

# print json.loads(flaw_file.readline())['impact_product']

for line in flaw_file.readlines():
    line = json.loads(line)
    # print line['impact_product']
    line['title'] = line['title'].replace('"', "'").replace('<td>', '')
    line['detail'] = line['detail'].replace('"', "'").replace('<td>', '')

    try:
        c.execute(insert_sql % (line['CNVD-ID'], line['denle'], line['time'], line['impact_product'], line['title'], line['detail']))
    except Exception as e:
        print e
        # print line
conn.commit()