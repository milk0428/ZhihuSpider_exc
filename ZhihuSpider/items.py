# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ZhihuQuestionItem(scrapy.Item):
    #zhihu的问题item
    zhihu_id=scrapy.Field()
    topics=scrapy.Field()
    url=scrapy.Field()
    title=scrapy.Field()
    content=scrapy.Field()
    #下边两个通过question页面直接获取不到，所以这里不要
    #create_time=scrapy.Field()
    #update_time=scrapy.Field()
    answer_num=scrapy.Field()
    comments_num=scrapy.Field()
    watch_user_num=scrapy.Field()
    click_num=scrapy.Field()
    crawl_time=scrapy.Field()
    crawl_update_time=scrapy.Field()

class ZhihuAnswerItem(scrapy.Item):
    zhihu_id=scrapy.Field()
    url=scrapy.Field()
    question_id=scrapy.Field()
    author_id=scrapy.Field()
    content=scrapy.Field()
    praise_num=scrapy.Field()
    comments_num=scrapy.Field()
    create_time=scrapy.Field()
    update_time=scrapy.Field()
    crawl_time=scrapy.Field()
    crawl_update_time=scrapy.Field()