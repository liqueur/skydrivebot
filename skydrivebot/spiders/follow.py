#coding:utf-8

import torndb
import scrapy
import json
import re
from scrapy.spiders import Spider
from skydrivebot.items import ResourceItem, UserItem
from IPython import embed
from skydrivebot.settings import db

class FollowSpider(Spider):
    name = 'follow'
    allowed_domains = ['yun.baidu.com']
    wap_follow_url = 'http://yun.baidu.com/wap/share/home/followers?uk={uk}&third=0&start={start}'

    def start_requests(self):
        count = db.get('select count(id) as count from user')['count']
        if count:
            return [scrapy.FormRequest(self.wap_follow_url.format(uk=row['uk'], start=0), callback=self.parse)
                    for row in db.query('select * from user where share=0')]
        else:
            return [scrapy.FormRequest(self.wap_follow_url.format(uk=1208824379, start=0), callback=self.parse)]

    def parse(self, response):
        uk = re.findall(r'uk=(\d+)', response.request.url)[0]
        follower_total_count = int(re.findall(r"totalCount:\"(\d+)\"", response.body)[0])
        db.update('update user set follow=1 where uk=%s', uk)

        if follower_total_count > 0:
            urls = [self.wap_follow_url.format(uk=uk, start=start) for start in range(20, follower_total_count, 20)]

            for url in urls:
                yield scrapy.Request(url, callback=self.parse_follow)

            follow_uk_list = re.findall(r"follow_uk\\\":(\d+)", response.body)

            for uk in follow_uk_list:
                yield UserItem(uk=uk)
                yield scrapy.Request(self.wap_follow_url.format(uk=uk, start=0), callback=self.parse)

    def parse_follow(self, response):
        uk = re.findall(r'uk=(\d+)', response.request.url)[0]

        follow_uk_list = re.findall(r"follow_uk\\\":(\d+)", response.body)

        for uk in follow_uk_list:
            yield UserItem(uk=uk)
            yield scrapy.Request(self.wap_follow_url.format(uk=uk, start=0), callback=self.parse)
