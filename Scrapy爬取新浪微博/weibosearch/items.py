# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class WeiboItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    tale_name = 'weibo'

    id = Field()
    url = Field()
    content = Field()
    comment_count = Field()
    forward_count = Field()
    like_count = Field()
    posted_at = Field()
    user = Field()
    keyword = Field()
