#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-02-24 22:32:41
# Project: huxiu

from pyspider.libs.base_handler import *
import json
from pyquery import PyQuery as pq
import pandas as pd
import time
import numpy as np
import pymongo
from pyspider.libs.utils import md5string

client = pymongo.MongoClient('localhost', 27017)
db = client.Huxiu
mongo_collection = db.huxiu_news


class Handler(BaseHandler):
    crawl_config = {
        "headers": {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
    }

    # 修改taskid,避免只下载一个post请求
    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    @every(minutes=24 * 60)
    def on_start(self):
        for page in range(2, 2125):
            print("正在爬取第 %s 页" % page)
            self.crawl('https://www.huxiu.com/v2_action/article_list',
                       method='POST', data={'page': page},
                       callback=self.index_page, validate_cert=False)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        content = response.json['data']
        doc = pq(content)
        lis = doc('.mod-art').items()
        data = [{
            'title': item('.msubstr-row2').text(),
            'url': 'https://www.huxiu.com' + str(item('.msubstr-row2').attr('href')),
            'name': item('.author-name').text(),
            'write_time': item('.time').text(),
            'comment': item('.icon-cmt+ em').text(),
            'favorites': item('.icon-fvr+ em').text(),
            'abstract': item('.mob-sub').text()
        } for item in lis]
        print(data)
        return data

    def on_result(self, result):
        if result:
            self.save_to_mongo(result)

    def save_to_mongo(self, result):
        df = pd.DataFrame(result)
        content = json.loads(df.T.to_json()).values()
        if mongo_collection.insert_many(content):
            print("存储到mongodb成功")
            sleep = np.random.randint(1, 5)
            time.sleep(sleep)






