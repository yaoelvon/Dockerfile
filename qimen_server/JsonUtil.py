# coding: utf-8
import json
import logging

from jsoncompare import jsoncompare


def load_json_file(filename):
    with open(filename, "r") as fp:
        return json.load(fp)


def load_json(data):
    return json.loads(data)


def sort(data):
    if isinstance(data, list):
        new_list = []
        for i in xrange(len(data)):
            new_list.append(sort(data[i]))
        return sorted(new_list)

    elif isinstance(data, dict):
        new_dict = {}
        for key in sorted(data):
            new_dict[key] = sort(data[key])
        return new_dict

    else:
        return data


def pop(data, del_keys):
    if isinstance(data, list):
        new_list = []
        for i in xrange(len(data)):
            new_list.append(pop(data[i], del_keys))
        return new_list

    elif isinstance(data, dict):
        new_dict = {}
        for key in data.keys():
            if key not in del_keys:
                new_dict[key] = pop(data[key], del_keys)
        return new_dict
    else:
        return data


def new(data, add_keys):
    if isinstance(data, list):
        new_list = []
        for i in xrange(len(data)):
            new_list.append(new(data[i], add_keys))
        return new_list

    elif isinstance(data, dict):
        new_dict = {}
        for key in data.keys():
            if key in add_keys:
                new_dict[key] = new(data[key], add_keys)
        return new_dict
    else:
        return data


def are_same(expected, actual, ignore_order=True, excluded=None, included=None):
    expected = json.loads(json.dumps(expected))
    actual = json.loads(json.dumps(actual))

    if excluded:
        expected = pop(expected, excluded)
        actual = pop(actual, excluded)

    if included:
        expected = new(expected, included)
        actual = new(actual, included)

    if ignore_order:
        expected = sort(expected)
        actual = sort(actual)

    logging.info("Excluded: {0}".format(excluded))
    logging.info("Expected:{0}\n\nActual  :{1}".format(expected, actual))

    return compare(expected, actual)


def compare(expected, actual):
    ret = jsoncompare.are_same(expected, actual)
    logging.info(ret[1])
    return ret[0]


def get_dict_value(pattern, dict_data):
    if dict_data is None:
        return dict_data
    p = pattern.split('.')
    k = pattern.split('.')[0]
    v = dict_data.get(k)
    if len(p) > 1 and v is not None:
        return get_dict_value('.'.join(p[1:]), v)
    else:
        return v


def set_dict_value(pattern, dict_data, value):
    p = pattern.split('.')
    k = pattern.split('.')[0]
    if isinstance(dict_data, dict):
        v = dict_data.get(k)
    elif isinstance(dict_data, list):
        v = dict_data[k]
    else:
        return None

    if len(p) > 1:
        return set_dict_value('.'.join(p[1:]), v, value)
    else:
        dict_data[k] = value
