# -*- coding:utf-8 -*-
# __author__ = 'szj'
import time
import xlsxwriter
from Exe_dispatch.ReadCases import ReadCaseInfo


def report_data(data):
    """
    分页整理测试报告的数据
    :param data:
    :return:
    """

    case_list = data['cases_list']
    sum_case = 0
    for scl in case_list:
        sum_case += len(scl['sheet_value'])

    sheet_result = data['sheet_result']
    success_case_num = 0
    for r in sheet_result:
        success_case_num += r['result']['time']

    sheet_name = [i['sheet_name'] for i in data['sheet_result']]

    value = {"sum_case": sum_case, "success_case_num": success_case_num, "case_list": case_list,
             "sheet_result": sheet_result, "sheet_name": sheet_name}
    return value


class Report(ReadCaseInfo):
    """
    生成测试日报
    """
    def __init__(self, report_path, data, case_path):
        super(Report, self).__init__(case_path)
        self.workbook = xlsxwriter.Workbook(report_path)
        self.worksheet = self.workbook.add_worksheet("测试总况")
        self.data = report_data(data)
        self.info = self.project_info()

    def get_format(self, wd, option):
        """
        设置样式
        :param wd:
        :param option:
        :return:
        """
        return wd.add_format(option)

    def get_format_center(self, wd, num=1):
        """
        设置居中
        :param wd:
        :param num:
        :return:
        """
        return wd.add_format({'align': 'center', 'text_wrap': 1, 'border': num})

    @staticmethod
    def get_format_fail(wd, num=1):
        """
        设置失败的居中样式
        :param wd:
        :param num:
        :return:
        """
        return wd.add_format({'align': 'center', 'text_wrap': 1, 'border': num, 'bg_color': 'red'})

    @staticmethod
    def get_format_left(wd, num=1):
        """
        设置左对齐
        :param wd:
        :param num:
        :return:
        """
        return wd.add_format({'border': num, 'text_wrap': 1})

    @staticmethod
    def get_format_fail_left(wd, num=1):
        """
        设置失败样式左对齐
        :param wd:
        :param num:
        :return:
        """
        return wd.add_format({'border': num, 'text_wrap': 1, 'bg_color': 'red'})

    @staticmethod
    def reset_border(wd, num=1):
        """
        设置单元格边框样式
        :param wd:
        :param num:
        :return:
        """
        return wd.add_format({}).set_border(num)

    def pie(self):
        """
        生成饼形图
        :return:
        """
        chart = self.workbook.add_chart({'type': 'pie'})
        chart.add_series({
            'name': '接口测试统计',
            'categories': '=测试总况!$D$4:$D$5',
            'values': '=测试总况!$E$4:$E$5',
        })
        chart.set_title({'name': '接口测试统计'})
        chart.set_style(10)
        self.worksheet.insert_chart('A9', chart, {'x_offset': 25, 'y_offset': 10})

    def write_center(self, worksheet, cl, data, wd):
        """
        写入数据居中
        :param worksheet:
        :param cl:
        :param data:
        :param wd:
        :return:
        """
        return worksheet.write(cl, data, self.get_format_center(wd))

    def write_fail_center(self, worksheet, cl, data, wd):
        """
        写入fail数据居中
        :param worksheet:
        :param cl:
        :param data:
        :param wd:
        :return:
        """
        return worksheet.write(cl, data, self.get_format_fail(wd))

    def write_left(self, worksheet, cl, data, wd):
        """
        写入数据左对齐
        :param worksheet:
        :param cl:
        :param data:
        :param wd:
        :return:
        """
        return worksheet.write(cl, data, self.get_format_left(wd))

    # 写fail数据
    def write_fail_left(self, worksheet, cl, data, wd):
        """
        写入失败数据左对齐
        :param worksheet:
        :param cl:
        :param data:
        :param wd:
        :return:
        """
        return worksheet.write(cl, data, self.get_format_fail_left(wd))

    def totali(self):
        """
        测试总览
        :param path:
        :return:
        """
        nowTime = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        sumCase = self.data['sum_case']
        success_case_num = self.data['success_case_num']

        # 设置列的宽度
        self.worksheet.set_column("A:A", 15)
        self.worksheet.set_column("B:F", 20)

        # 设置行的高度
        self.worksheet.set_row(1, 30)
        self.worksheet.set_row(2, 30)
        self.worksheet.set_row(3, 30)
        self.worksheet.set_row(4, 30)
        self.worksheet.set_row(5, 30)

        define_format_H1 = self.get_format(self.workbook, {'bold': True, 'font_size': 18})
        define_format_H2 = self.get_format(self.workbook, {'bold': True, 'font_size': 16})
        define_format_H1.set_border(1)

        define_format_H2.set_border(1)
        define_format_H1.set_align("center")
        define_format_H2.set_align("center")
        define_format_H2.set_bg_color("blue")
        define_format_H2.set_color("#ffffff")

        self.worksheet.merge_range('A1:F1', '测试报告总概况', define_format_H1)
        self.worksheet.merge_range('A2:F2', '测试概括', define_format_H2)
        self.worksheet.merge_range('A3:A6', '项目图片', self.get_format_center(self.workbook))

        self.write_center(self.worksheet, "B3", '项目名称', self.workbook)
        self.write_center(self.worksheet, "B4", '接口版本', self.workbook)
        self.write_center(self.worksheet, "B5", '脚本语言', self.workbook)
        self.write_center(self.worksheet, "B6", '测试人员', self.workbook)

        self.write_center(self.worksheet, "D3", "接口总数", self.workbook)
        self.write_center(self.worksheet, "D4", "通过总数", self.workbook)
        self.write_center(self.worksheet, "D5", "失败总数", self.workbook)
        self.write_center(self.worksheet, "D6", "测试日期", self.workbook)
        self.write_center(self.worksheet, "F3", "接口通过率", self.workbook)
        self.worksheet.merge_range('F4:F6', '=TEXT(E4/E3,"0.00%")', self.get_format_center(self.workbook))

        self.write_center(self.worksheet, "C3", self.info['project_name'], self.workbook)
        self.write_center(self.worksheet, "C4", self.info['version'], self.workbook)
        self.write_center(self.worksheet, "C5", "python", self.workbook)
        self.write_center(self.worksheet, "C6", self.info['tester'], self.workbook)
        self.write_center(self.worksheet, "E3", sumCase, self.workbook)
        self.write_center(self.worksheet, "E4", success_case_num, self.workbook)
        self.write_center(self.worksheet, "E5", sumCase - success_case_num, self.workbook)
        self.write_center(self.worksheet, "E6", nowTime, self.workbook)
        self.pie()

    def detail(self):
        """
        测试详细数据
        :return:
        """
        sheetName = self.data['sheet_name']
        sheetResult = self.data['sheet_result']
        case_list = self.data['case_list']
        for s in range(len(sheetName)):
            worksheet = self.workbook.add_worksheet(sheetName[s])
            # 设置列的宽度
            worksheet.set_column("A:A", 10)
            worksheet.set_column("B:B", 20)
            worksheet.set_column("C:C", 10)
            worksheet.set_column("D:I", 30)
            worksheet.set_column("J:L", 15)

            style = {'bold': True, 'font_size': 18, 'align': 'center', 'valign': 'vcenter', 'bg_color': 'blue', 'font_color': '#ffffff'}
            worksheet.merge_range('A1:L1', '测试详情', self.get_format(self.workbook, style))
            self.write_center(worksheet, "A2", '用例ID', self.workbook)
            self.write_center(worksheet, "B2", '接口名称', self.workbook)
            self.write_center(worksheet, "C2", '请求方式', self.workbook)
            self.write_center(worksheet, "D2", 'URL', self.workbook)
            self.write_center(worksheet, "E2", '参数', self.workbook)
            self.write_center(worksheet, "F2", '请求报文', self.workbook)
            self.write_center(worksheet, "G2", '断言判断', self.workbook)
            self.write_center(worksheet, "H2", '断言结果', self.workbook)
            self.write_center(worksheet, "I2", '响应报文', self.workbook)
            self.write_center(worksheet, "J2", '响应码', self.workbook)
            self.write_center(worksheet, "K2", '响应时间(ms)', self.workbook)
            self.write_center(worksheet, "L2", '测试结果', self.workbook)
            test_result_list = sheetResult[s]['result']['test_result_list']
            result_data_list = sheetResult[s]['result']['result_data_list']
            response_list = sheetResult[s]['result']['response_list']
            res_code_list = sheetResult[s]['result']['res_code_list']
            res_time_list = sheetResult[s]['result']['res_time_list']
            sheet_value = case_list[s]['sheet_value']
            for i in range(len(sheet_value)):
                worksheet.set_row(i + 2, 30)
                if test_result_list[i] == 'fail':
                    self.write_fail_center(worksheet, "A" + str(i + 3), sheet_value[i]['case_id'],
                                           self.workbook)
                    self.write_fail_left(worksheet, "B" + str(i + 3), sheet_value[i]['case_name'],
                                         self.workbook)
                    self.write_fail_center(worksheet, "C" + str(i + 3), sheet_value[i]['method'],
                                           self.workbook)
                    self.write_fail_left(worksheet, "D" + str(i + 3), sheet_value[i]['url'], self.workbook)
                    self.write_fail_left(worksheet, "E" + str(i + 3), sheet_value[i]['param'], self.workbook)
                    self.write_fail_left(worksheet, "F" + str(i + 3), sheet_value[i]['body'], self.workbook)
                    self.write_fail_left(worksheet, "G" + str(i + 3), sheet_value[i]['checks'], self.workbook)
                    self.write_fail_left(worksheet, "H" + str(i + 3), str(result_data_list[i]), self.workbook)
                    self.write_fail_left(worksheet, "I" + str(i + 3), str(response_list[i]), self.workbook)
                    self.write_fail_center(worksheet, "J" + str(i + 3), res_code_list[i], self.workbook)
                    self.write_fail_center(worksheet, "K" + str(i + 3), res_time_list[i], self.workbook)
                    self.write_fail_center(worksheet, "L" + str(i + 3), test_result_list[i], self.workbook)
                else:
                    self.write_center(worksheet, "A" + str(i + 3), sheet_value[i]['case_id'], self.workbook)
                    self.write_left(worksheet, "B" + str(i + 3), sheet_value[i]['case_name'], self.workbook)
                    self.write_center(worksheet, "C" + str(i + 3), sheet_value[i]['method'], self.workbook)
                    self.write_left(worksheet, "D" + str(i + 3), sheet_value[i]['url'], self.workbook)
                    self.write_left(worksheet, "E" + str(i + 3), sheet_value[i]['param'], self.workbook)
                    self.write_left(worksheet, "F" + str(i + 3), sheet_value[i]['body'], self.workbook)
                    self.write_left(worksheet, "G" + str(i + 3), sheet_value[i]['checks'], self.workbook)
                    self.write_left(worksheet, "H" + str(i + 3), str(result_data_list[i]), self.workbook)
                    self.write_left(worksheet, "I" + str(i + 3), str(response_list[i]), self.workbook)
                    self.write_center(worksheet, "J" + str(i + 3), res_code_list[i], self.workbook)
                    self.write_center(worksheet, "K" + str(i + 3), res_time_list[i], self.workbook)
                    self.write_center(worksheet, "L" + str(i + 3), test_result_list[i], self.workbook)

        self.workbook.close()

