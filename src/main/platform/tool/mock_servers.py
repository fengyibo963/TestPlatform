# -*- coding: utf-8 -
import time
import datetime
import pytz
import random
from string import Template
from flask import *
from src.main.platform.common.logger import Log
from src.main.mysql.func import *

log = Log()


class MockReturn:

    def replace_param(self):
        Time_Ymd = datetime.datetime.now().strftime('%Y-%m-%d')  # 当前日期
        Time_HMS = datetime.datetime.now().strftime('%H:%M:%S')  # 当前时间(无日期)
        Time_YmdHMS = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 当前时间
        Time_YmdHMSf = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')  # 当前时间(精确到秒)
        Time_stamp_10 = int(time.time())  # 当前10位时间戳
        Time_stamp_13 = round(time.time() * 1000)  # 当前13位时间戳
        Time_utc_cn = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))  # 上海时间utc的标准时间
        Time_iso_cn = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()  # 上海时间utc的iso格式
        Time_utc_in = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))  # 印度时间utc的标准时间
        Time_iso_in = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()  # 印度时间utc的iso格式
        Time_utc_0tz = datetime.datetime.now(pytz.timezone('UTC'))  # 0时区utc的标准时间
        Time_iso_0tz = datetime.datetime.now(pytz.timezone('UTC')).isoformat()  # 0时区utc的iso格式
        # print(pytz.country_timezones('gb'))  # 根据国家简称查询支持城市,根据iso3166_code
        Random_number_0 = random.randint(0, 9)
        Random_number_10 = random.randint(10, 99)
        Random_number_100 = random.randint(100, 999)
        Random_number_1000 = random.randint(1000, 9999)
        Random_number_10000 = random.randint(10000, 99999)

        parm_list = {"Time_Ymd": Time_Ymd, "Time_HMS": Time_HMS, "Time_YmdHMS": Time_YmdHMS,
                     "Time_YmdHMSf": Time_YmdHMSf, "Time_stamp_10": Time_stamp_10, "Time_stamp_13": Time_stamp_13,
                     "Time_utc_cn": Time_utc_cn, "Time_iso_cn": Time_iso_cn, "Time_utc_in": Time_utc_in,
                     "Time_iso_in": Time_iso_in, "Time_utc_0tz": Time_utc_0tz, "Time_iso_0tz": Time_iso_0tz,
                     "Random_number_0": Random_number_0, "Random_number_10": Random_number_10,
                     "Random_number_100": Random_number_100, "Random_number_1000": Random_number_1000,
                     "Random_number_10000": Random_number_10000}  # 响应字段替换列表
        return parm_list

    # 请求正常时的正确返回
    def correct_return(self, result):  # result="{'resp_body': , 'resp_status': , 'resp_headers': }"

        # 获取响应body,并将其替换输出
        body = result['resp_body']
        body_template = Template(body)
        resp_body = body_template.substitute(self.replace_param())

        # 获取响应headers,并将其替换输出
        headers = result['resp_headers']
        headers_template = Template(headers)
        resp_headers = headers_template.substitute(self.replace_param())

        if resp_headers == "":
            response_headers = None  # 如果没有配置resp_headers,则返回空字符
        else:
            response_headers = json.loads(resp_headers)  # 将结果转为字典用于响应返回

        if resp_body == "":
            response_body = None  # 如果没有配置resp_body,则返回空字符
        else:
            response_body = json.loads(resp_body)  # 将结果转为字典用于响应返回

        resp = Response(json.dumps(response_body))
        resp.status = result['resp_status']  # status直接使用str字符即可
        resp.headers = response_headers
        return resp

    # 异常请求的错误返回
    def error_return(self, error):
        resp = Response(json.dumps({"success": False, "error_message": error}))
        resp.status = "400 Bad Request"
        return resp


class MockErrorHandle(MockReturn):

    # 对于mock配置的url验证
    def url_judge(self, parm_url):
        url_list = []  # 查询数据库mock配置中存在的所有url并写入url_list=["","",""] url不能出现/
        for url in database_func('mock_servers', 'get', 'all_url'):
            url_list.append(url[0])
        if parm_url in url_list:  # 如果请求的url存在于url_list即为该mock存在，否则按照404响应返回
            return True
        else:
            log.info('MockServer请求url不存在,响应404')
            abort(404)  # url不存在

    # 对于mock配置的method验证
    def method_judge(self, parm_method, methods):
        if parm_method == methods:  # 如果请求方式与mock配置的请求方式一致即为请求成功，否则按照405响应返回
            return True
        else:
            log.info('MockServer请求方法错误,响应405')
            abort(405)  # 请求方式错误

    # 对于mock配置的is_available验证
    def is_available_judge(self, is_available):
        if is_available == 1:
            return True
        else:
            log.info('MockServer请求url未启用,响应404')
            abort(404)  # 如果mock不启用，报404

    # 请求的错误处理-headers必填缺少(headers配置不为空时)  headers_parm=["","",""]
    def headers_lack_judge(self, request, headers_parm):
        # 如果请求参数缺少(参数列表缺少任意一个)，按错误处理
        for p in headers_parm:
            if p not in request.headers:
                return self.error_return(p)
            else:
                if request.json.get(p) == "":  # 如果请求参数值为“”
                    return self.error_return("param " + p + "is error")
                else:
                    pass
        return True

    # 请求的错误处理-参数格式
    def body_format_judge(self, request):
        try:
            json.dumps(request.json)
        except ValueError:
            log.info('mock请求body参数格式错误,没有按照json格式传参')
            return self.error_return('')
        else:
            return True

    # 请求的错误处理-body必填参数缺少(参数配置不为空时)  body_parm=["","",""]
    def body_lack_judge(self, request, body_parm):
        # 如果请求参数缺少(参数列表缺少任意一个)，按错误处理
        for p in body_parm:
            if p not in request.json:
                return self.error_return(p)
            else:
                if request.json.get(p) == "":  # 如果请求参数值为“”(布尔值、int类型为空时会按照不符合json格式处理掉)
                    return self.error_return("param " + p + "is error")
                else:
                    pass
        return True


class MockServer(MockErrorHandle):
    def __init__(self, url, request):
        self.request = request
        self.url = url

    # 构建mock_server服务
    def mock_server(self):
        if self.url_judge(self.url) is True:
            mock = database_func('mock_servers', 'get', 'first_by_url', self.url)
            if self.method_judge(self.request.method, mock['methods']) is True:
                if self.is_available_judge(mock['is_available']) is True:
                    resp = database_func('mock_response', 'get', 'first_default_by_mockId', mock['id'])
                    response = {"resp_body": resp['body'], "resp_status": resp['status'],
                                "resp_headers": resp['headers']}
                    time.sleep(mock['delay'] / 1000)  # 延时响应/ms
                    return self.correct_return(response)

    # 构建mock_server服务，验证请求参数(验证是否满足json-是否有参数未传-是否有必填项为空)
    def mock_server_request(self):
        if self.url_judge(self.url) is True:
            mock = database_func('mock_servers', 'get', 'first_by_url', self.url)
            if self.method_judge(self.request.method, mock['methods']) is True:
                if self.is_available_judge(mock['is_available']) is True:
                    resp = database_func('mock_response', 'get', 'first_default_by_mockId', mock['id'])
                    response = {"resp_body": resp['body'], "resp_status": resp['status'],
                                "resp_headers": resp['headers']}

                    headers_lack_judge = self.headers_lack_judge(self.request, list(response.headers_parm))
                    if headers_lack_judge is True:
                        # 再判断如果请求body为空时，请求body参数配置是否也为空（均为空按照参数校验通过处理）
                        if not self.request.json and list(response.body_parm) == []:
                            log.info('mock请求未设置任何参数,直接返回结果')
                            return self.correct_return(response)
                        else:
                            # 再获取请求body格式是否错误(满足json格式)结果
                            body_format_judge = self.body_format_judge(self.request)
                            if body_format_judge is True:
                                # 再获取请求body参数是否缺少(以及必填项是否填写)结果
                                body_lack_judge = self.body_lack_judge(self.request, list(response.body_parm))
                                if body_lack_judge is True:
                                    time.sleep(mock['delay'] / 1000)  # 延时响应/ms
                                    return self.correct_return(response)
                                else:
                                    return body_lack_judge
                            else:
                                return body_format_judge
                    else:
                        return headers_lack_judge
