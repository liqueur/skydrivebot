# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    origin = scrapy.Field()
    uk = scrapy.Field()

class ResourceItem(scrapy.Item):
    origin = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    feed_time = scrapy.Field()
    feed_username = scrapy.Field()
    feed_user_uk = scrapy.Field()
    size = scrapy.Field()
    v_cnt = scrapy.Field()
    d_cnt = scrapy.Field()
    t_cnt = scrapy.Field()
