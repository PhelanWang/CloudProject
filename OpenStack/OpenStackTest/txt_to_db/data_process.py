# coding: utf-8

import json
import sqlite3


data = open('./data/new_data.txt').readlines()
print json.loads(data[0]).keys()


'''
CNVD-ID
title
impact_product
detail
time
denle
'''
'''
CREATE TABLE VDSM_flaw_scan (
  id INTEGER PRIMARY KEY NOT NULL,
  cve_id TEXT NOT NULL, CNVD-ID
  f_name TEXT  NULL, title
  f_severity TEXT  NULL, denle
  f_describe TEXT  NULL, detail
  pub_date TEXT  NULL, time
  ud_date TEXT  NULL, time
  product TEXT  NULL , impact_product
  version TEXT  NULL, impact_product
  influence TEXT  NULL impact_product);
'''

insert_sql = 'INSERT INTO "%s" VALUES(%d,"%s","%s","%s","%s","%s","%s","%s","%s","%s");'
'''
Ovirt_flaw_scan    VDSM_flaw_scan     kvm_flaw_scan      libvirt_flaw_scan
'''

conn = sqlite3.connect('data/cloud.db')
c = conn.cursor()
id = 100
for item in data:
    item_json = json.loads(item)

    item_json['title'] = item_json['title'].replace('"', "'").replace('<td>', '')
    item_json['detail'] = item_json['detail'].replace('"', "'").replace('<td>', '')

    try:

        if 'ovirt' in item_json['title'] or 'oVirt' in item_json['title']:
            c.execute(insert_sql % ('Ovirt_flaw_scan',id, item_json['CNVD-ID'], item_json['title'], item_json['denle'], item_json['detail'],
                                    item_json['time'], item_json['time'], item_json['impact_product'],
                                    item_json['impact_product'], item_json['impact_product']))

        if 'kvm' in item_json['title'] or 'KVM' in item_json['title']:
            c.execute(insert_sql % ('kvm_flaw_scan',id, item_json['CNVD-ID'], item_json['title'], item_json['denle'], item_json['detail'],
                                    item_json['time'], item_json['time'], item_json['impact_product'],
                                    item_json['impact_product'], item_json['impact_product']))

        if 'VDSM' in item_json['title']:
            c.execute(insert_sql % ('VDSM_flaw_scan',id, item_json['CNVD-ID'], item_json['title'], item_json['denle'], item_json['detail'],
                                    item_json['time'], item_json['time'], item_json['impact_product'],
                                    item_json['impact_product'], item_json['impact_product']))

        if 'libvirt' in item_json['title']:
            c.execute(insert_sql % ('libvirt_flaw_scan',id, item_json['CNVD-ID'], item_json['title'], item_json['denle'], item_json['detail'],
                                    item_json['time'], item_json['time'], item_json['impact_product'],
                                    item_json['impact_product'], item_json['impact_product']))
        id += 1
    except Exception, e:
        print item_json['title']
        print item_json['detail']
    finally:
        conn.commit()