#coding:utf-8

import scrapy
import json
import re
from scrapy.spiders import Spider
from skydrivebot.items import ResourceItem, UserItem

class SkyDriveSpider(Spider):
    name = 'sds'
    allowed_domains = ['yun.baidu.com']
    bd_short_share_url = 'http://yun.baidu.com/s/{shorturl}'
    bd_share_url = 'http://yun.baidu.com/share/link?uk={uk}&shareid={shareid}'
    share_url = 'http://yun.baidu.com/pcloud/feed/getsharelist?auth_type=1&start={start}&limit=60&query_uk={uk}'
    share_referer_url = 'http://yun.baidu.com/share/home?uk={uk}&view=share'
    wap_follow_url = 'http://yun.baidu.com/wap/share/home/followers?uk={uk}&third=0&start={start}'
    album_url = 'http://yun.baidu.com/pcloud/album/info?uk={uk}&album_id={album_id}'
    start_urls = [wap_follow_url.format(uk=1208824379, start=0)]

    def parse(self, response):
        uk = re.findall(r'uk=(\d+)', response.request.url)[0]
        yield scrapy.Request(self.share_url.format(uk=uk, start=0), callback=self.parse_share_count)
        follower_total_count = int(re.findall(r"totalCount:\"(\d+)\"", response.body)[0])
        if follower_total_count > 0:
            urls = [self.wap_follow_url.format(uk=uk, start=start) for start in range(0, follower_total_count, 20)]

            for url in urls:
                yield scrapy.Request(url, callback=self.parse_follow)

    def parse_follow(self, response):
        follow_uk_list = re.findall(r"follow_uk\\\":(\d+)", response.body)

        for uk in follow_uk_list:
            yield UserItem(uk=uk)
            yield scrapy.Request(self.wap_follow_url.format(uk=uk, start=0), callback=self.parse)

    def parse_share_count(self, response):
        total_count = int(json.loads(response.body)['total_count'])

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
