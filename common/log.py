# -*- coding:utf-8 -*-
# __author__ = 'szj'
import logging
import os

src_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
filepath = os.path.join(src_path, 'log/syserror.log')


class Logger(object):
    """
    定义输出日志的级别以及位置
    :return:
    """
    def __init__(self, filename):
        # 创建logger对象
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(logging.INFO)

        # 创建处理器，输出日志到log_file
        file_handler = logging.FileHandler(filepath, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 创建处理器，输出日志到控制台
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)

        # 定义处理器的输出格式
        fmt_log = '%(asctime)s %(module)s %(levelname)s %(message)s'
        date_fmt = '%Y%m%d %H:%M:%S'
        formatter = logging.Formatter(fmt=fmt_log, datefmt=date_fmt)
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # 添加处理器到logger对象
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
