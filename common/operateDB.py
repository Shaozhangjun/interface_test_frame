# -*- coding:utf-8 -*-
# __author__ = 'szj'

"""
定义对数据库基本操作的封装：增删改查
"""

import psycopg2
import pymssql
import cx_Oracle
from common.log import Logger

sy_log = Logger(__name__)


class DBInterface(object):
    """
    封装数据库操作的类
    """

    def __init__(self, dbtype, config):
        """
        初始化连接，根据数据库类型选择对应的配置连接
        :param dbtype: str 数据库类型
        :param config: dict 具体配置
        """
        try:
            if dbtype == 'oracle':
                self.__host = config['host']
                self.__db = config['database']
                self.__user = config['user']
                self.__pwd = config['password']
                self.__port = config['port']
                self.__conn = cx_Oracle.connect(
                    "%s/%s@%s/%s" % (self.__user, self.__pwd, self.__host, self.__db))
                self.__cur = self.__conn.cursor()
            elif dbtype == 'sqlserver':
                self.__host = config['host']
                self.__db = config['database']
                self.__user = config['user']
                self.__pwd = config['password']
                self.__port = config['port']
                self.__conn = pymssql.connect(database=self.__db, user=self.__user, password=self.__pwd,
                                              host=self.__host, port=self.__port)
                self.__cur = self.__conn.cursor()
            else:
                self.__host = config['host']
                self.__db = config['database']
                self.__user = config['user']
                self.__pwd = config['password']
                self.__port = config['port']
                self.__conn = psycopg2.connect(database=self.__db, user=self.__user, password=self.__pwd,
                                               host=self.__host, port=self.__port)
                self.__cur = self.__conn.cursor()

        except (psycopg2.Error, cx_Oracle.Error, pymssql.Error, Exception) as error:
            raise error

    def op_sql(self, condition):
        """
        定义数据操作，包含删除，更新，插入
        :param condition: str SQL语句，该通用方法可用来替代 update one, delete one, insert into one
        """
        try:
            sy_log.logger.info(condition)
            self.__cur.execute(condition)  # 执行sql语句
            self.__conn.commit()  # 提交游标数据
        except (psycopg2.Error, cx_Oracle.Error, pymssql.Error, Exception) as error:
            self.__conn.rollback()  # 执行回滚操作
            sy_log.logger.info(error)
            return {"synyi_test_frame_track": '执行sql出错，用例失败'}

    def select_sql(self, condition):
        """
        定义数据查询操作
        :param condition: SQL语句
        :return: 字典形式的单条查询结果
        """
        try:
            sy_log.logger.info(condition)
            self.__cur.execute(condition)  # 执行sql语句
            select_results = self.__cur.fetchall()  # 获取结果
            data = []
            if len(select_results) > 0:
                for row in select_results:  # 遍历结果，将数据添加到data列表中
                    data.append(row)
            result = {'data': data}
            return result
        except (psycopg2.Error, cx_Oracle.Error, pymssql.Error, Exception) as error:
            sy_log.logger.info(error)
            return {"synyi_test_frame_track": '执行sql出错，用例失败'}

    def __del__(self):
        """
        定义关闭数据库连接
        :return: None
        """
        if self.__cur is not None:
            self.__cur.close()  # 关闭游标
        if self.__conn is not None:
            self.__conn.close()  # 关闭数据库连接
