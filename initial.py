#coding:utf-8

import torndb

db = torndb.Connection('127.0.0.1:3306', 'sds', user='root', password='britten')

db.update('delete from user')
db.update('delete from resource')
db.update('delete from index_log')
db.update('delete from status')

db.insert('insert into status (share_running) values (0)')
