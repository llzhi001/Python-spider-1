#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-12-30 15:45:45
# Project: tripadvisor

from pyspider.libs.base_handler import *
import pymongo


class Handler(BaseHandler):
    crawl_config = {
    }

    client = pymongo.MongoClient('localhost')
    db = client['trip']

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.tripadvisor.cn/Attractions-g186338-Activities-c47-London_England.html',
                   callback=self.index_page, validate_cert=False)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('.listing_title > a').items():
            self.crawl(each.attr.href, callback=self.detail_page, validate_cert=False)

        next = response.doc('.pagination .nav.next').attr.href
        self.crawl(next, callback=self.index_page, validate_cert=False)

    @config(priority=2)
    def detail_page(self, response):
        url = response.url
        name = response.doc('.h1').text()
        rating = response.doc('a > .reviewCount').text()
        address = response.doc('.contactInfo > .address > span > span').text()
        phone = response.doc('.contact > .is-hidden-mobile > div').text()
        duration = response.doc('#component_3 > div > div:nth-child(3) > div').text()

        return {
            "url": url,
            "title": response.doc('title').text(),
            'name': name,
            'rating': rating,
            'address': address,
            'phone': phone,
            'duration': duration,
        }

    def on_result(self, result):
        if result:
            self.save_to_mongo(result)

    def save_to_mongo(self, result):
        if self.db['London'].insert(result):
            print('Saved to mongo ', result)






