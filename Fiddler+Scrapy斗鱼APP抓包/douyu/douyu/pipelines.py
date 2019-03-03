# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.utils.project import get_project_settings
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import os

class DouyuPipeline(ImagesPipeline):
    IMAGES_STORE = get_project_settings().get('IMAGES_STORE')

    # 获取图片链接，并发送图片请求
    def get_media_requests(self, item, info):
        image_url = item['image_link']
        yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_path = [x['path'] for ok, x in results if ok]

        os.rename(self.IMAGES_STORE + '\\' + image_path[0],
                  self.IMAGES_STORE + '\\' + item['nickname'] + '.jpg')

        item['image_path'] = self.IMAGES_STORE + '\\' + item['nickname']

        return item

