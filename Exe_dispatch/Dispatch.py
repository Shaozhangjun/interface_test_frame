# -*- coding:utf-8 -*-
# __author__ = 'szj'
import os
import time
import re
from Exe_dispatch.sendEmail import SendEmail
from Exe_dispatch.Report import Report, report_data
from common.log import Logger
from Exe_dispatch.ExecuteCases import Execute


sy_log = Logger(__name__)


def dispatch(path, load_type=0, *case_suites):
    """
    调度执行文件
    :param path:
    :param load_type: 0：执行指定的文件， 1：执行文件夹下的所有文件
    :param case_suites: 可选参数，接受参数为列表对象，内容为sheet页名称。不传入，默认执行所有Case，传入则执行列表中指定的sheet页
    :return:
    """
    now_time = time.strftime("%Y-%m-%d %H_%M", time.localtime())  # 获取当前时间，并转化为指定的格式
    abs_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if re.findall('/', path):
        os_win = '/'
    else:
        os_win = '\\'
    if load_type == 0:
        if os.path.isdir(path):  # 判断是否为文件夹
            sy_log.logger.info("输入的路径与加载方式不一致，请检查")
            sy_log.logger.info("load_type: " + str(load_type) + "---> 执行指定文件")
            sy_log.logger.info("path: " + path)

        if path.endswith('.xlsx'):  # 是否是EXCEL文件
            excel_name = path.split(os_win)[-1].split('.')[0]
            report_path = os.path.join(abs_path, excel_name + '_' + now_time + '_result.xlsx')

            sy_log.logger.info("------------------- 开始执行指定文件：%s -------------------" % excel_name)

            if len(case_suites) > 0:  # 判断是否指定sheet页执行
                exe_result = Execute().execute_case(path, case_suites[0])
            else:
                exe_result = Execute().execute_case(path)

            sy_log.logger.info("------------------- 执行结束，生成报告 -------------------")

            # 按照固定的路径生成报告
            new_reportstyle = Report(report_path, exe_result, path)
            new_reportstyle.totali()
            new_reportstyle.detail()

            sy_log.logger.info("------------------- 生成报告成功，通过邮件发送报告 -------------------")
            SendEmail(report_path, exe_result, path).send_email(report_path)
        else:
            sy_log.logger.info("文件不是EXCEL，无法执行")
    else:
        if os.path.isdir(path):
            dir_name = path.split(os_win)[-1]  # 获取文件夹名称
            report_path = os.path.join(abs_path, 'testResult' + os_win + dir_name)

            sy_log.logger.info("------------------- 开始执行文件夹  %s -------------------" % dir_name)

            files = os.listdir(path)  # 获取路径下的所有文件及文件夹
            # 判断报告路径是否存在，不存在就创建文件夹
            if not os.path.exists(report_path):
                os.makedirs(report_path)
            email_data_sum = {"sum_case": 0, "success_case_num": 0}
            email_report_path = []
            file_path, result_value, emailNewPath = '', '', ''
            for file in files:
                new_path = path + os_win + file
                # 判断是否为文件夹，文件夹不执行
                if not os.path.isdir(new_path):
                    if re.findall('\.xlsx', new_path, re.I):
                        sy_log.logger.info("------------------- 开始执行  %s ------------------- " % file)
                        result_value = Execute().execute_case(new_path)
                        file_path = os.path.join(report_path, file + '_' + now_time + '_result.xlsx')
                        new_report_style = Report(file_path, result_value, report_path)
                        new_report_style.totali()
                        new_report_style.detail()
                        email_data = report_data(result_value)
                        email_data_sum['sum_case'] += email_data['sum_case']
                        email_data_sum['success_case_num'] += email_data['success_case_num']
                        emailNewPath = new_path
                        email_report_path.append(file_path)
                    else:
                        sy_log.logger.info("文件不是EXCEL，无法执行\n")
            sy_log.logger.info("------------------- 生成报告成功，通过邮件发送报告 -------------------")
            SendEmail(file_path, result_value, report_path).send_email(emailNewPath)
        else:
            sy_log.logger.info("出入的路径与加载方式不一致，请检查")
            sy_log.logger.info("load_type: " + str(load_type) + "---> 执行指定文件")
            sy_log.logger.info("path: " + path)
