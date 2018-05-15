# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
from  ZhihuSpider.util.common import extract_num
from ZhihuSpider.settings import SQL_DATETIME_FORMAT

class ZhihuQuestionItem(scrapy.Item):
    #zhihu的问题item
    #该item在zhihu_spider.py中是通过item_loader方式获取，每个元素返回的均为list对象，故需处理合并
    zhihu_id=scrapy.Field()
    topics=scrapy.Field()
    url=scrapy.Field()
    title=scrapy.Field()
    content=scrapy.Field()
    answer_num=scrapy.Field()
    comments_num=scrapy.Field()
    watch_user_num=scrapy.Field()
    click_num=scrapy.Field()
    crawl_time=scrapy.Field()

    # 为使得pipelines中数据库插入模块通用多个item的插入操作，故在每一个item中定义插入模块，返回插入语句及插入数据元组
    @property
    def get_insert_sql(self):
        insert_sql="""
                insert into zhihu_question(zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time)
                VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
                ON DUPLICATE KEY UPDATE content=VALUES(content),answer_num=VALUES(answer_num),comments_num=VALUES(comments_num),watch_user_num=VALUES(watch_user_num),click_num=VALUES(click_num),crawl_time=VALUES(crawl_time)
        """

        # 该item在zhihu_spider.py中是通过item_loader方式获取，每个元素返回的均为list对象，故需在此处理合并
        zhihu_id=self["zhihu_id"][0]
        topics=",".join(self["topics"])
        url=self["url"][0]
        title=self["title"][0]
        content=self["content"][0]
        answer_num=int(self["answer_num"][0].replace(",","")) if "answer_num" in self else 0  #这个有可能无
        # 样式如'6 条评论'，需借助自己写的工具类处理
        comments_num=extract_num(self["comments_num"][0])
        watch_user_num=int(self["watch_user_num"][0])
        click_num=int(self["click_num"][1])
        #注意在settings中设置mysql格式，在此导入
        crawl_time=datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        #注意数据类型为元组
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

    #为使得pipelines中数据库插入模块通用多个item的插入操作，故在每一个item中定义插入模块，返回插入语句及插入数据元组
    @property
    def get_insert_sql(self):
        insert_sql="""
                insert into zhihu_answer(zhihu_id,url,question_id,author_id,content,praise_num,comments_num,create_time,update_time,crawl_time)
                VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
                ON DUPLICATE KEY UPDATE content=VALUES(content),praise_num=VALUES(praise_num),comments_num=VALUES(comments_num),update_time=VALUES(update_time),crawl_time=VALUES(crawl_time)
        """

        # 该item在zhihu_spider.py中是直接赋值，故不需像qusetion中那样
        zhihu_id=self["zhihu_id"]
        url=self["url"]
        question_id=self["question_id"]
        author_id=self["author_id"]
        content=self["content"]
        praise_num=self["praise_num"]
        comments_num=self["comments_num"]
        create_time=self["create_time"]
        update_time=self["update_time"]
        crawl_time=self["crawl_time"]
        #注意要是元组
        params=(zhihu_id,url,question_id,author_id,content,praise_num,comments_num,create_time,update_time,crawl_time)
        return insert_sql,params