# -*- coding:utf-8 -*-
# __author__ = 'szj'
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from common.log import Logger
from Exe_dispatch.Report import Report

sy_log = Logger(__name__)


class SendEmail(Report):

    def send_email(self, report_path):
        """
        发送测试日报邮件
        :param report_path:
        :return:
        """
        try:
            emailInfo = self.info['emile']
            if emailInfo:
                if emailInfo['on_off'] == 'on':
                    smtpserver = emailInfo['smtpserver']
                    user = emailInfo['user']
                    password = emailInfo['password']  # 授权码非邮箱登录密码
                    receivers = emailInfo['receivers']
                    message = MIMEMultipart()
                    message['Subject'] = emailInfo['subject']
                    message['From'] = user
                    message['To'] = ",".join(receivers)

                    # 获取总览数据，添加邮件正文
                    sumCase = self.data['sum_case']
                    success_case_num = self.data['success_case_num']
                    fail_num = sumCase - success_case_num
                    pass_result = "%.2f%%" % (success_case_num / sumCase * 100)

                    content = f"此次接口测试一共运行用例为：{sumCase}，通过个数为：{success_case_num}，失败个数为：{fail_num}，" \
                              f"通过率为：{pass_result}, 报告详情请查看附件！"
                    body = MIMEText(content, _subtype="plain", _charset="utf-8")
                    message.attach(body)

                    # 添加附件
                    if isinstance(report_path, list):
                        for r in report_path:
                            att = MIMEText(open(r, 'rb').read(), "base64", "utf-8")
                            att["Content-Type"] = "application/octet-stream"
                            filename = r.split('\\')[-1]
                            att["Content-Disposition"] = 'attachment; filename="%s"' % filename
                            message.attach(att)
                    else:
                        att = MIMEText(open(report_path, 'rb').read(), "base64", "utf-8")
                        att["Content-Type"] = "application/octet-stream"
                        filename = report_path.split('\\')[-1]
                        att["Content-Disposition"] = 'attachment; filename="%s"' % filename
                        message.attach(att)

                    # 连接发送邮件（smtplib模块基本使用格式）
                    smtp = smtplib.SMTP_SSL(smtpserver, port=465)
                    smtp.login(user, password)
                    smtp.sendmail(user, receivers, message.as_string())
                    smtp.quit()
                    sy_log.logger.info("------------------- 邮件发送成功，请注意查收邮件 -------------------")
                else:
                    sy_log.logger.info("------------------- 邮件未配置，不通过邮件发送测试结果 -------------------")
        except Exception as error:  # 程序异常
            sy_log.logger.info(error)  # 打印日志
            sy_log.logger.info("------------------- 程序出错，邮件未成功发送 -------------------")
            raise error

