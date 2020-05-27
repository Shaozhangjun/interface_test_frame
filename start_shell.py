# -*- coding:utf-8 -*-
# __author__ = 'szj'
from Exe_dispatch.Dispatch import dispatch
import click
import sys
import os


@click.command()
@click.option('-t', '--testcase', required=True, help=u'测试用例文件，或者一个目录（执行该目录下所有用例文件）')
@click.option('-l', '--load_type', help=u'load_type int类型参数，0：执行指定的文件，此时，配置文件CasePath 填写的为文件的绝对路径，'
                                        u'若不需要执行全部的excel文件，传入case_suites，case_suites为数组类型的参数，元素为此sheet'
                                        u'页的名称，不传则执行全部文件。当load_type=1，配置文件的CasePath填写的为文件夹的绝对路径，'
                                        u'此时会执行文件夹下所有的Excel文件')
def start(testcase, load_type):
    dispatch(testcase, load_type)


if __name__ == '__main__':
    if os.name == 'nt':
        start(sys.argv[1:])
    else:
        start()
