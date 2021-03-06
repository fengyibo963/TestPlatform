# -*- coding: utf-8 -
from src.main.platform.tool.pairs import Pairs as FuncPairs
from src.main.platform.interface.public.public import *


class Pairs:

    def get_pairs(self, request):
        input = request.json.get("input")

        # 根据参数检查结果判断,如果检查通过则正常处理
        check_result = CheckParm().get_pairs(input)
        if check_result[0] is True:
            data = Func().get_pairs(input)
            return right_response(data)
        else:
            return error_response(check_result[1])


class Func:

    def get_pairs(self, input):
        # data = {"pairs": json.dumps(FuncOrthogonal().all_pairs(input)).encode('utf-8').decode('unicode_escape')}
        result = FuncPairs().all_pairs(input)
        data = {"num": result[0], "pairs": result[1]}
        return data


class CheckParm:

    def get_pairs(self, input):
        if type(input) != list:
            return False, "param is error, param not filled or type error"
        else:
            return True, None

