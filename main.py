# -*- coding: utf-8 -
import os
from flask import *
from api.api import *
from src.mock_servers import MockServer
app = Flask(__name__)

# 当前脚本所在的文件绝对路径
cur_path = os.path.dirname(os.path.realpath(__file__))
# 将当前路径设置为python的临时环境变量，用于命令执行,需要设置是因为项目存在多处相互调用
os.putenv("PYTHONPATH", cur_path)


# 本身服务接口
@app.route('/<path:url>', methods=['GET', 'POST', 'HEAD', 'PUT', 'PATCH', 'DELETE'])
def mock_server_mock_show_lists(url):
    log('request', request)
    response = API(url, request).api()
    log('response', request, response)
    return response


# mock服务的接口
# 默认string(只能传str字符),int(只能传int字符)、float(只能传float字符)、path(可以接收任意字符串,包括路径带/)、uuid(只能传uuid字符串)
@app.route('/mock/<path:url>', methods=['GET', 'POST', 'HEAD', 'PUT', 'PATCH', 'DELETE'])
def create_mock(url):
    log('request', request)
    response = MockServer(url, request).mock_server()
    log('response', request, response)
    return response


def create_db_table():
    # 使用os.path.join拼接地址
    case_path = os.path.join(cur_path, "db")
    print(os.path.join(case_path, "func.py"))
    os.system('python3 {}'.format(os.path.join(case_path, "func.py")))


if __name__ == '__main__':
    create_db_table()
    app.run(host='0.0.0.0', port=5000, debug=True)
