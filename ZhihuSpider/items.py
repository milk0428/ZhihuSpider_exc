# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
from  ZhihuSpider.util.common import extract_num
from ZhihuSpider.settings import SQL_DATE_FORMAT,SQL_DATETIME_FORMAT

class ZhihuspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ZhihuQuestionItem(scrapy.Item):
    #zhihu的问题item
    #该item在zhihu_spider.py中是通过item_loader方式获取，每个元素返回的均为list对象，故需处理合并
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

    def get_insert_sql(self):
        insert_sql="""
                insert into zhihu_question(zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time)
                VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
        """

        # 该item在zhihu_spider.py中是通过item_loader方式获取，每个元素返回的均为list对象，故需在此处理合并
        zhihu_id=self["zhihu_id"][0]
        topics=",".join(self["topics"])
        url=self["url"][0]
        title=self["title"][0]
        content=self["content"][0]
        answer_num=int(self["answer_num"][0].replace(",",""))  #这个有可能无
        # 样式如'6 条评论'，需借助自己写的工具类处理
        comments_num=extract_num(self["comments_num"][0])
        watch_user_num=int(self["watch_user_num"][0])
        click_num=int(self["click_num"][1])
        #注意在settings中设置mysql格式，在此导入
        crawl_time=datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params=(zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time)
        return insert_sql,params

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
