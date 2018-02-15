#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


def dict_to_kv_list(data):
    """
       Take a dict and return a list of k=v pairs

        Input data:
        {'a': 1, 'b': 2}

        Return data:
        ['a=1', 'b=2']
    """
    return ['='.join(str(e) for e in x) for x in data.items()]


def list_to_dict(lst, separator='='):
    """
       This converts a list of ["k=v"] to a dictionary {k: v}.
    """
    kvs = [i.split(separator) for i in lst]
    return {k: v for k, v in kvs}


class FilterModule(object):
    def filters(self):
        return {
            'dict_to_kv_list': dict_to_kv_list,
            'list_to_dict': list_to_dict
        }
