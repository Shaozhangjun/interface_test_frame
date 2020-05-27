# -*- coding:utf-8 -*-
# __author__ = 'szj'
import time


def rd(f, n):
    """
    保留几位小数，并且不四舍五入
    :param n:
    :param f:
    :return:
    """
    if n <= 0:
        return len(str(f).split('.')[0])
    if f < 0:
        index = n + 3
    else:
        index = n + 2
    return float(str(f)[0:index])


def time2long(s_time, fmt="yyyy-mm-dd hh:mm:ss"):
    """
    格式化时间戳
    :param s_time: 传入的时间
    :param fmt:
    :return:
    """
    s_time = str(s_time)
    if (s_time.startswith('"') and s_time.endswith('"')) or (s_time.startswith("'") and s_time.endswith("'")):
        s_time = s_time[1:-1]
    try:
        if fmt.lower() == "yyyy-mm-dd hh:mm:ss":
            t = time.mktime(time.strptime(s_time, '%Y-%m-%d %H:%M:%S'))  # 1482286976.0
            return rd(t, 0)
        elif fmt.lower() == r"yyyy/mm/dd hh:mm:ss":
            pass
    except Exception:
        return s_time


def str2bool(s_bool):
    """
    如果str跟bool有关系就转换为bool类型,没有就返回原始str
    :param s_bool:
    :return:
    """
    d_bools = {'false': False, 'true': True}
    try:
        res = d_bools[s_bool.lower()]
    except Exception:
        return s_bool
    else:
        return res


def pretreated(actual_value, except_value):
    """
    预处理比较参数
    :param actual_value:
    :param except_value:
    :return:
    """
    D_NULL = {'null': None, 'NULL': None, 'Null': None, '[]': None, '{}': None}
    if actual_value is None:
        except_value = time2long(except_value)
        except_value = str2bool(except_value)
        except_value = D_NULL.get(except_value, except_value)
        return {"actual_value": actual_value, "except_value": except_value}
    else:
        actual_value = time2long(actual_value)
        except_value = time2long(except_value)
        actual_value = str2bool(actual_value)
        except_value = str2bool(except_value)
        actual_value = D_NULL.get(actual_value, actual_value)
        except_value = D_NULL.get(except_value, except_value)
        return {"actual_value": actual_value, "except_value": except_value}


def assert_return(judge, actual_value, except_value):
    if judge:
        result = {'result': True, 'actual_value': actual_value, 'except_value': except_value}
    else:
        result = {'result': False, 'actual_value': actual_value, 'except_value': except_value}
    return result


def assert_data(compare, actual_value, except_value):
    """"
    :param compare: 传入str
    :param actual_value: 传入str
    :param except_value: 传入str
    :return: 断言结果
    """
    pretreated_value = pretreated(actual_value, except_value)
    actual_value = pretreated_value['actual_value']
    except_value = pretreated_value['except_value']
    if compare == '==':  # 判断是否相等
        judge = str(actual_value) == str(except_value)
        result = assert_return(judge, actual_value, except_value)
    elif compare in ('>', '>=', '<', '<='):
        if except_value is None or actual_value is None:
            result = {'result': False, 'actual_value': actual_value, 'except_value': except_value}
        elif isinstance(except_value, bool) or isinstance(actual_value, bool):
            result = {'result': False, 'actual_value': actual_value, 'except_value': except_value}
        else:
            if compare == '>':
                judge = int(actual_value) > int(except_value)
            elif compare == '>=':
                judge = int(actual_value) >= int(except_value)
            elif compare == '<':
                judge = int(actual_value) < int(except_value)
            else:
                judge = int(actual_value) <= int(except_value)
            result = assert_return(judge, actual_value, except_value)
    elif compare in('len_<', 'len_<=', 'len_>', 'len_>=', 'len_=='):
        if isinstance(except_value, bool) or isinstance(actual_value, bool):
            result = {'result': False, 'actual_value': actual_value, 'except_value': except_value}
        else:
            if except_value is None or actual_value is None:
                except_value = 0 if except_value is None else except_value
                actual_value = 0 if actual_value is None else actual_value
                if compare == 'len_<':
                    judge = int(actual_value) < int(except_value)
                elif compare == 'len_<=':
                    judge = int(actual_value) <= int(except_value)
                elif compare == 'len_>':
                    judge = int(actual_value) > int(except_value)
                elif compare == 'len_>=':
                    judge = int(actual_value) >= int(except_value)
                else:
                    judge = int(actual_value) == int(except_value)
            else:
                if compare == 'len_<':
                    judge = len(eval(actual_value)) < int(except_value)
                elif compare == 'len_<=':
                    judge = len(eval(actual_value)) <= int(except_value)
                elif compare == 'len_>':
                    judge = len(eval(actual_value)) > int(except_value)
                elif compare == 'len_>=':
                    judge = len(eval(actual_value)) >= int(except_value)
                else:
                    judge = len(eval(actual_value)) == int(except_value)
            result = assert_return(judge, actual_value, except_value)
    else:
        judge = str(actual_value) != str(except_value)
        result = assert_return(judge, actual_value, except_value)
    return result
    # elif compare == 'contain':  # 判断actual_value是不是except_value的子字符串
    #     try:
    #         pretreated_value = pretreated(actual_value, except_value)
    #         actual_value = pretreated_value['actual_value']
    #         except_value = pretreated_value['except_value']
    #         if actual_value == except_value:
    #             result = {'result': True, 'actual_value': actual_value, 'except_value': except_value}
    #             return result
    #         else:
    #             if actual_value in ContainsHelper(except_value):
    #                 result = {'result': True, 'actual_value': actual_value, 'except_value': except_value}
    #             else:
    #                 result = {'result': False, 'actual_value': actual_value, 'except_value': except_value}
    #             return result
    #     except:
    #         result = {'result': False, 'actual_value': actual_value, 'except_value': except_value}
    #         return result
    # elif compare == 'contain_by':  # 判断actual_value是不是except_value的子字符串
    #     try:
    #         pretreated_value = pretreated(actual_value, except_value)
    #         actual_value = pretreated_value['actual_value']
    #         except_value = pretreated_value['except_value']
    #         if actual_value == except_value:
    #             result = {'result': True, 'actual_value': actual_value, 'except_value': except_value}
    #             return result
    #         else:
    #             if except_value in ContainsHelper(actual_value):
    #                 result = {'result': True, 'actual_value': actual_value, 'except_value': except_value}
    #             else:
    #                 result = {'result': False, 'actual_value': actual_value, 'except_value': except_value}
    #             return result
    #     except:
    #         result = {'result': False, 'actual_value': actual_value, 'except_value': except_value}
    #         return result
    # elif compare == 'uncontain':
    #     try:
    #         pretreated_value = pretreated(actual_value, except_value)
    #         actual_value = pretreated_value['actual_value']
    #         except_value = pretreated_value['except_value']
    #         if actual_value not in ContainsHelper(except_value):
    #             result = {'result': True, 'actual_value': actual_value, 'except_value': except_value}
    #         else:
    #             result = {'result': False, 'actual_value': actual_value, 'except_value': except_value}
    #         return result
    #     except:
    #         result = {'result': False, 'except_value': except_value, 'actual_value': ''}
    #         return result

