# -*- coding:utf-8 -*-
# __author__ = 'szj'
import re
import sys
import xlrd
import json
from common.util import get_token
from common.log import Logger
from common.operateDB import DBInterface

sy_log = Logger(__name__)


def set_inter_value(key_value, temp_value, db_config):
    """
    预处理中间变量
    :param key_value: 预处理后的中间变量
    :param temp_value: Excel中写的中间变量
    :param db_config: 数据库配置
    :return:
    """
    for t_value in temp_value.split(';\n'):
        temp = t_value.split('=')
        if re.findall('\$.*?{', temp[1]):
            if '$sql{' in temp[1]:
                dbtype = 'pg'
                dbc = db_config['pg']
                sql = re.findall('(?<=\$sql{)[\s\S]+(?=})', temp[1], re.I)
            elif '$orasql{' in temp[1]:
                dbtype = 'oracle'
                dbc = db_config['oracle']
                sql = re.findall('(?<=\$orasql{)[\s\S]+(?=})', temp[1], re.I)
            elif '$mssql{' in temp[1]:
                dbtype = 'sqlserver'
                dbc = db_config['sqlserver']
                sql = re.findall('(?<=\$mssql{)[\s\S]+(?=})', temp[1], re.I)
            else:
                sy_log.logger.info("没有找到支持的数据库类型，请检查")
                sys.exit(0)
            sy_log.logger.info("sql为：%s" % str(sql[0]))
            temp_v = DBInterface(dbtype, dbc).select_sql(sql[0])
            if temp_v['data']:
                key_value[temp[0].strip()] = temp_v['data'][0][0]
            else:
                key_value[temp[0].strip()] = temp_v['data']
        else:
            key_value[temp[0].strip()] = temp[1].strip()
    return key_value


class ReadCaseInfo(object):
    def __init__(self, path):
        self.excel = xlrd.open_workbook(path)
        try:
            self.sheet_config = self.excel.sheet_by_name("config")
        except IOError:
            sy_log.logger.info("没有找到config")
            sys.exit(0)

    def read_db_config(self, db_cell):
        """
        读取数据库配置
        :param db_cell: 列表类型，读取数据库配置
        :return:
        """
        db_config = {}
        for db in db_cell:
            config = {}
            db_type = db["db_type"]
            data_base = self.sheet_config.cell_value(db["row"], db["column"])
            if data_base:
                data_base = data_base.strip()
                try:
                    data_base = json.loads(data_base)
                except Exception:
                    sy_log.logger.info("序列化data_base出错")
                    sys.exit(0)
                for key, value in data_base.items():
                    if value:
                        config[key.lower()] = value.strip()
                    else:
                        config[key.lower()] = ''
                db_config[db_type] = config
        if len(db_config) < 1:
            sy_log.logger.info("没有配置数据库，请检查")
            sys.exit(0)
        return db_config

    def load_excel_values(self, *case_suites):
        """
        按需加载Excel中的数据
        :param case_suites: 可选参数，可以预处理指定sheet页的数据
        :return:
        """
        if case_suites:
            sheet_cases = []
            for suite in case_suites[0]:
                if suite in self.excel.sheet_names():
                    sheet = self.excel.sheet_by_name(suite)
                    sheet_value = {'sheet_name': suite, 'sheet_values': sheet._cell_values[1:]}
                    sheet_cases.append(sheet_value)
                else:
                    sy_log.logger.info("未找到指定的sheet页: %s" % str(suite))
                    sys.exit(0)
        else:
            sheets = self.excel.sheets()
            if self.excel.nsheets < 2:
                sy_log.logger.info("文件sheet页至少两个")
                sys.exit(0)
            else:
                sheet_cases = [{'sheet_name': sheets[i].name, 'sheet_values': sheets[i]._cell_values[1:]} for
                               i in range(self.excel.nsheets) if sheets[i].name != 'config']
        return sheet_cases

    def project_info(self):
        """
        测试项目的信息
        :return:
        """
        emile = self.sheet_config.cell_value(7, 1)
        if emile:
            try:
                sy_log.logger.info("email配置为：%s" % emile)
                emile = json.loads(emile)
            except Exception:
                sy_log.logger.info("序列化email失败，无法发送测试报告")
                sys.exit(0)

        project_info = {
            'project_name': self.sheet_config.cell_value(2, 1),
            'version': self.sheet_config.cell_value(3, 1),
            'tester': self.sheet_config.cell_value(4, 1),
            'emile': emile
        }
        return project_info

    def pretreated_case(self, *case_suites):
        """
        预处理用例
        :param case_suites: 可选参数，可以预处理指定sheet页的数据
        :return:
        """
        if case_suites:
            all_case_values = self.load_excel_values(case_suites[0])
        else:
            all_case_values = self.load_excel_values()
        # 测试域名
        test_url = self.sheet_config.cell_value(1, 1).strip()
        if not test_url:
            sy_log.logger.info("测试环境URL为空")
            sys.exit(0)

        # 接口超时时间设置
        timeout = int(self.sheet_config.cell_value(5, 1))

        # 获取请求权限
        token = self.sheet_config.cell_value(6, 1)
        if token:
            token = token.strip()
            sy_log.logger.info("token %s" % token)
            try:
                info = json.loads(token)
            except Exception:
                sy_log.logger.info("序列化token出错")
                sys.exit(0)
            Authorization = get_token(info['url'], info['headers'], info['data'])
            sy_log.logger.info("Authorization: %s" % Authorization)
        else:
            Authorization = ""

        # 数据库连接配置
        db_cell = [{"row": 8, "column": 1, "db_type": "pg"}, {"row": 9, "column": 1, "db_type": "Oracle"},
                   {"row": 10, "column": 1, "db_type": "SQLServer"}]
        db_config = self.read_db_config(db_cell)

        # 测试数据处理
        inter_value = []
        all_cases = []
        for sheet_cases in all_case_values:
            sy_log.logger.info("正在加载并预处理 %s" % sheet_cases['sheet_name'])
            sheet_case_values = []
            sheet_inter_values = {'sheet_name': sheet_cases['sheet_name'], 'inter_value': {}}
            for case in sheet_cases['sheet_values']:
                if_exe = case[2].strip()
                if if_exe.lower() == 'yes':
                    case_id = case[0]
                    case_name = case[1]
                    method = case[3].strip()
                    api = case[4].strip()
                    # url
                    if api.startswith('http'):
                        url = api
                    else:
                        url = test_url + api
                    # 处理header，替换token
                    header = case[5].strip()
                    if re.findall("'", header):
                        header = header.replace("'", "\"")
                    if 'Authorization' in header:
                        header_dir = json.loads(header)
                        header_dir['Authorization'] = Authorization
                        header = json.dumps(header_dir)
                    param = case[6].strip()
                    body = case[7].strip()
                    exe_before = case[8]
                    status_except = int(case[9])
                    check_before = case[10].strip()
                    checks = case[11].strip()
                    check_after = case[12].strip()
                    case_data = {'case_id': case_id, 'case_name': case_name, 'url': url, 'header': header,
                                 'param': param, 'method': method, 'body': body,
                                 'exe_before': exe_before, 'status_except': status_except,
                                 'check_before': check_before, 'checks': checks, 'check_after': check_after}
                    # 预处理中间变量
                    if case[13]:
                        temp_value = set_inter_value(sheet_inter_values['inter_value'], case[13], db_config)
                        sheet_inter_values['inter_value'] = temp_value
                        case_data['inter_value'] = case[13]
                    sheet_case_values.append(case_data)
            inter_value.append(sheet_inter_values)
            all_cases.append({'sheet_name': sheet_cases['sheet_name'], 'sheet_value': sheet_case_values})
        return all_cases, inter_value, db_config, timeout

# if __name__ == '__main__':
