# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import torndb
from skydrivebot.items import UserItem, ResourceItem
from IPython import embed

db = torndb.Connection('localhost:3306', 'sds', user='root', password='britten')

class UserPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, UserItem):
            sql = 'insert into user (origin, uk) values (%s, %s)'
            try:
                db.insert(sql, 'baiduyun', item['uk'])
            except:
                pass

        return item

class ResourcePipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, ResourceItem):
            sql = ('insert into resource'
            '(origin, url, title, feed_time, feed_username, feed_user_uk, size, v_cnt, d_cnt, t_cnt)'
            'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')

            try:
                db.insert(sql, 'baiduyun',
                          item.get('url'),
                          item.get('title'),
                          item.get('feed_time'),
                          item.get('feed_username'),
                          item.get('feed_user_uk'),
                          item.get('size'),
                          item.get('v_cnt'),
                          item.get('d_cnt'),
                          item.get('t_cnt'))
            except Exception as e:
                embed()

        return item
