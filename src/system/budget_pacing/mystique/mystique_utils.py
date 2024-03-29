# Copyright Yahoo, Licensed under the terms of the Apache license . See LICENSE file in project root for terms.

import numpy as np


def get_beginning_of_modulo_location(arr, modulo):
    """Returns the location of the first element in the latest sequence that is equal or shorter than the modulo value
    Example: if len(arr)==16 and modulo==7, this method will return 14"""
    l = len(arr)
    mod = l % modulo
    if mod == 0:
        mod = modulo
    return len(arr) - mod


def get_arr_sum_of_last_tuple_item(arr):
    last_tuple_item_arr = [item[-1] for item in arr]
    return sum(last_tuple_item_arr)


def get_arr_sum_of_last_tuple_item_from_modulo_location(arr, modulo):
    start_loc = get_beginning_of_modulo_location(arr, modulo)
    sliced_arr = arr[start_loc:]
    return get_arr_sum_of_last_tuple_item(sliced_arr)


def get_average_per_size(arr, size):
    """returns array of averages of length arr/size(+1) of averages of every size elements"""
    chunks = [arr[i:(i + size)] for i in range(0, len(arr), size)]
    return [sum(chunk) / len(chunk) for chunk in chunks]


