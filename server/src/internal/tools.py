import copy
from collections import defaultdict
from typing import Dict, Any


def sum_int_dicts(*dicts) -> Dict[Any, int]:
    sum_dict = defaultdict(int)
    for dic in dicts:
        dic = copy.deepcopy(dic)
        for k, v in dic.items():
            sum_dict[k] += v
    return sum_dict


def deduct_int_dicts(from_dict: Dict[Any, int], deduct_dict: Dict[Any, int]) -> Dict[Any, int]:
    from_dict = copy.deepcopy(from_dict)
    deduct_dict = copy.deepcopy(deduct_dict)

    for key, value in deduct_dict.items():
        if key in from_dict:
            from_dict[key] -= deduct_dict[key]
            if not from_dict[key]:
                del from_dict[key]

    return from_dict


def is_int_dict_in_dict(dic: Dict[Any, int], in_dic: Dict[Any, int]) -> bool:
    dic = copy.deepcopy(dic)
    in_dic = copy.deepcopy(in_dic)

    for key, value in dic.items():
        if not value:
            continue

        if key not in in_dic:
            return False

        if in_dic[key] < value:
            return False

    return True


def order_dict_by_value(dict_: Dict):
    if len(dict_) <= 0:
        return dict_
    dict_ = copy.deepcopy(dict_)
    return {k: v for k, v in sorted(dict_.items(), key=lambda item: item[1])}
