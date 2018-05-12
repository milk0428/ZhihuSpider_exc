# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors

class ZhihuspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class MysqlTwistedPipline(object):
    def __init__(self,dbpool):
        self.dbpool=dbpool

    #读取settings.py中配置的数据库信息
    @classmethod
    def from_settings(cls,settings):
        #以字典方式传递数据库参数，注意该字典的参数名字要和MySQLdb.connect中的参数名字一致
        dbparms=dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool=adbapi.ConnectionPool("MySQLdb",**dbparms)
        return cls(dbpool)

    #使用twisted将mysql插入变成异步执行
    def process_item(self , item , spider):
        query=self.dbpool.runInteraction(self.do_insert,item)
        #处理异步存入数据库时候的错误
        query.addErrback(self.handle_error,item,spider)

    #执行具体的插入
    def do_insert(self,cursor,item):
        insert_sql,params = item.get_insert_sql()
        cursor.execute(insert_sql,params)
        #不用使用commit()函数，会自动提交

    #处理异步插入的异常。其中item和spider参数为自定义，可以删去，则调用的时候省略。
    def handle_error(self,failure,item,spider):
        print(failure)