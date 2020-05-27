# -*- coding:utf-8 -*-
# __author__ = 'szj'
import re
from common.log import Logger
from Exe_core.assertfunction import assert_data
from Exe_core.check import check_var, check_select

sy_log = Logger(__name__)


def standby(standby_res, response):
    """
    获取接口实际值
    :param standby_res:
    :param response:
    :return:
    """
    try:
        if re.findall('\$[\w.]+', standby_res, re.I):
            res_path = re.findall('(?<=\$)[\w.]+', standby_res, re.I)
            # 取出路径具体的key
            path_key = res_path[0].split('.')
            # 序列化接口返回的数据
            res = eval(response) if isinstance(response, str) else response
            # 遍历key列表，递归获取value的值
            try:
                for key in path_key:
                    key = int(key) if re.findall('^\d+$', key) else key
                    res = res[key]
            except Exception:
                sy_log.logger.info("按照路径从返回值中取值错误")
                return {"track": False, "res": res}
            return {"track": True, "res": res}

        elif re.findall('(?<=\$\()[\s\S]+(?=\))', standby_res, re.I):
            res = re.findall('(?<=\$\()[\s\S]+(?=\))', standby_res, re.I)
            res = res[0] if len(res) > 0 else 0
            return {"track": True, "res": res}
        else:
            return {"track": False, "res": '未找到校验值'}
    except Exception as error:
        raise error


def except_check(check_value, key_value, db_config):
    # 判断是否要依赖其他接口返回数据
    if re.findall('\$var{', check_value, re.I):
        check_value = check_var(check_value, key_value)
        if "synyi_test_frame_track" in check_value:
            return check_value

    # 判断是否存在$sql
    if re.findall('\$sql{[\s\S]+?}', check_value, re.I):
        check_value = check_select(check_value, 'pg', db_config['pg'])

    elif re.findall('\$orasql{[\s\S]+?}', check_value, re.I):
        check_value = check_select(check_value, 'pg', db_config['pg'])

    elif re.findall('\$mssql{[\s\S]+?}', check_value, re.I):
        check_value = check_select(check_value, 'pg', db_config['pg'])

    return check_value


def compare(check_params, response, key_value, db_config):
    """
    校验结果判断
    :param db_config:
    :param key_value:
    :param check_params: 要处理的参数
    :param response: 要处理的返回
    :return: 返回参数
    """
    params_list = check_params.split(';\n')
    x = 1
    result_list = []
    result_data = []
    for param in params_list:
        # 判断断言方法
        assert_method = re.findall('[=!]+|[<>=]+|len_[><=]+', param)
        if assert_method:
            assert_method = assert_method[0]
        else:
            result_list.append(False)
            result_data.append({'result': False, 'result_data': '没有获取到断言方式，请检查用例'})
            continue
        compare_list = param.split(assert_method)
        # 校验值
        standby_res = compare_list[0].strip()
        # 期望值
        check_value = compare_list[1].strip()

        # 获取接口返回的真实校验值
        res = standby(standby_res, response)
        if not res['track']:
            result_list.append(False)
            result_data.append({'result': False, 'actual': response, 'check': check_value})
            continue
        else:
            actual_res = res['res']

        # 获取真实的期望值
        except_value = except_check(check_value, key_value, db_config)
        if "synyi_test_frame_track" in except_value:
            result_list.append(False)
            result_data.append({'result': False, 'actual': actual_res, 'check': check_value})
            continue

        result = assert_data(assert_method, actual_res, except_value)
        sy_log.logger.info("断言参数" + str(x) + "：" + str(result['actual_value']) + " " + assert_method + " " + str(
                result['except_value']))
        result_list.append(result['result'])
        result_data.append(result)
        x += 1

    if False in result_list:
        result = {'result': False, 'result_data': result_data}
        return result
    else:
        result = {'result': True, 'result_data': result_data}
        return result
