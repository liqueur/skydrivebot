# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
from skydrivebot.items import UserItem, ResourceItem

db = MongoClient().sds

class UserPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, UserItem):
            db.user.update({'origin':'baiduyun'},
                           {'$addToSet':{'uk_list':item.get('uk')}},
                           True)

        return item

class ResourcePipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, ResourceItem):
            db.resource.insert(dict(item))

        return item
