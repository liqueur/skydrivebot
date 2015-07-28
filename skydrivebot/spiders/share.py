#coding:utf-8

import torndb
import scrapy
import json
import re
from scrapy.spiders import Spider
from skydrivebot.items import ResourceItem
from skydrivebot.settings import db
from scrapy import log

class ShareSpider(Spider):
    name = 'share'
    allowed_domains = ['yun.baidu.com']
    bd_short_share_url = 'http://yun.baidu.com/s/{shorturl}'
    bd_share_url = 'http://yun.baidu.com/share/link?uk={uk}&shareid={shareid}'
    share_url = 'http://yun.baidu.com/pcloud/feed/getsharelist?auth_type=1&start={start}&limit=60&query_uk={uk}'
    share_referer_url = 'http://yun.baidu.com/share/home?uk={uk}&view=share'

    def start_requests(self):
        rows = db.query('select uk from user where share=0 limit 10')
        for row in rows:
            db.update('update user set share=1 where uk=%s', row['uk'])
        return [scrapy.FormRequest(self.share_url.format(uk=row['uk'], start=0), callback=self.parse) for row in rows]

    def parse(self, response):
        uk = re.findall(r'uk=(\d+)', response.request.url)[0]
        try:
            total_count = int(json.loads(response.body)['total_count'])
        except KeyError as e:
            log.msg(e)
            db.update('update user set share=2 where uk=%s', uk)
            return

        if total_count > 0:
            uk = re.findall(r'query_uk=(\d+)', response.request.url)[0]
            urls = [self.share_url.format(uk=uk, start=start).encode('utf-8')
                    for start in range(0, total_count, 60)]

            for url in urls:
                yield scrapy.Request(url,
                                     callback=self.parse_share,
                                     headers={'Referer':self.share_referer_url.format(uk=uk)})

    def parse_share(self, response):
        shared = json.loads(response.body)
        uk = re.findall(r'uk=(\d+)', response.request.url)[0]

        def gen_link(record):
            if 'album' in record:
                return False
            elif 'shorturl' in record and len(record['shorturl']):
                return self.bd_short_share_url.format(shorturl=record['shorturl'])
            elif 'shareid' in record and len(record['shareid']):
                return self.bd_share_url.format(uk=uk, shareid=record['shareid'])
            else:
                return False

        for record in shared['records']:
            if gen_link(record):
                yield ResourceItem(origin='baiduyun',
                                   url=gen_link(record),
                                   title=record['title'],
                                   feed_time=record['feed_time'] / 1000,
                                   feed_username=record['username'],
                                   feed_user_uk=uk,
                                   size=record['filelist'][0]['size'],
                                   v_cnt=record['vCnt'],
                                   d_cnt=record['dCnt'],
                                   t_cnt=record['tCnt'])
