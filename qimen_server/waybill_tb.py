# coding: utf-8
from __future__ import unicode_literals
import logging
import uuid
import json
import urllib
import bottle
from bottle import HTTPError
from bottle.ext import sqlalchemy
from database import Base, engine
from database import WaybillResp

tb = bottle.Bottle(catchall=False)

plugin = sqlalchemy.Plugin(
    engine,  # SQLAlchemy engine created with create_engine function.
    Base.metadata,  # SQLAlchemy metadata, required only if create=True.
    keyword='db',  # Keyword used to inject session database in a route (default 'db').
    create=True,  # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
    commit=True,  # If it is true, plugin commit changes after route is executed (default True).
    use_kwargs=False
    # If it is true and keyword is not defined,
    # plugin uses **kwargs argument to inject session database (default False).
)

tb.install(plugin)


def handle_taobao_waybill(db):
    logging.debug('-------------HANDLE TAOBAO WAYBILL GET-------------')
    GET_MAPPING = {
        '0': tb_create_waybill_normal,
        '1': tb_create_waybill_missing_part_big_pen,
        '2': tb_create_waybill_missing_full_big_pen,
        '3': tb_create_waybill_missing_waybill_code,
        '4': tb_create_waybill_without_balance
    }
    CANCEL_MAPPING = {
        '9': tb_cancel_response_normal,
        '8': tb_cancel_response_fail
    }
    q = dict(bottle.request.query)
    logging.debug('/router/rest query: {}'.format(q))
    body = bottle.request.body.getvalue()
    logging.debug('/router/rest body: {}'.format(body))

    method = q['method']
    if method == 'taobao.wlb.waybill.i.get':
        body_request = urllib.unquote(body.split('=')[-1].replace('+', ''))
        json_request = json.loads(body_request)
        logging.debug('/router/rest json request: {}'.format(json.dumps(json_request, indent=4, ensure_ascii=False)))
        package_id = json_request['trade_order_info_cols'][0]['package_id']
        package_ids = [e['package_id'] for e in json_request['trade_order_info_cols']]

        func = GET_MAPPING.get(package_id[-3]) or tb_create_waybill_normal
        waybills = [func(pid, db) for pid in package_ids]
        if package_id[-3] == '4':
            return json.dumps(tb_create_waybill_without_balance())
        return json.dumps(tb_get_response(waybills))

    elif method == 'taobao.wlb.waybill.i.cancel':
        return json.dumps(tb_cancel_response_normal())
    elif method == 'taobao.user.seller.get':
        return json.dumps(tb_seller_get_response())
    elif method == 'taobao.wlb.waybill.i.search':
        return json.dumps(tb_search_response_normal())


@tb.get('/waybill')
def taobao_waybill(db):
    logging.debug('-------------GET TAOBAO WAYBILL-------------')
    q = dict(bottle.request.query)
    logging.debug(q)
    logging.debug(bottle.request.body.getvalue().decode('utf-8'))
    order_code = q.get('order_code')
    record = db.query(WaybillResp).filter_by(key=order_code).first()
    if record:
        return record.body
    else:
        return HTTPError(404, None)


@tb.post('/reset')
def tb_reset(db):
    [db.delete(item) for item in db.query(WaybillResp).all()]

def tb_get_response(waybills):
    return {
        "wlb_waybill_i_get_response": {
            "waybill_apply_new_cols": {
                "waybill_apply_new_info": waybills
            }
        }
    }


def tb_create_waybill_normal(package_id, db):
    waybill_code = str(uuid.uuid4()).split('-')[-1]
    ret = {
        "short_address": "SHANGHAI",
        "trade_order_info": {
            "package_id": package_id
        },
        "waybill_code": waybill_code,
        "package_center_code": "VWMS_CENTER_CODE",
        "package_center_name": "微仓网络发运中心",
        "print_config": "VWMS_CONFIG",
        "shipping_branch_code": "VWMS_1234",
        "consignee_branch_name": "SHANGHAI_PUDONG",
        "shipping_branch_name": "PUDONG_ZHANGJIANG",
        "consignee_branch_code": "VWMS_4321"
    }
    logging.debug('Waybill normal: {}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
    db.add(WaybillResp(package_id, json.dumps(ret)))
    return ret


def tb_create_waybill_missing_part_big_pen(package_id, db):
    waybill_code = str(uuid.uuid4()).split('-')[-1]
    ret = {
        "short_address": "SHANGHAI",
        "trade_order_info": {
            "package_id": package_id
        },
        "waybill_code": waybill_code,
        "package_center_code": "VWMS_CENTER_CODE",
        "package_center_name": "",
        "print_config": "VWMS_CONFIG",
        "shipping_branch_code": "VWMS_1234",
        "consignee_branch_name": "SHANGHAI_PUDONG",
        "shipping_branch_name": "PUDONG_ZHANGJIANG",
        "consignee_branch_code": "VWMS_4321"
    }
    logging.debug('Waybill no part big pen: {}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
    db.add(WaybillResp(package_id, json.dumps(ret)))
    return ret


def tb_create_waybill_missing_full_big_pen(package_id, db):
    waybill_code = str(uuid.uuid4()).split('-')[-1]
    ret = {
        "short_address": "",
        "trade_order_info": {
            "package_id": package_id
        },
        "waybill_code": waybill_code,
        "package_center_code": "",
        "package_center_name": "",
        "print_config": "VWMS_CONFIG",
        "shipping_branch_code": "VWMS_1234",
        "consignee_branch_name": "SHANGHAI_PUDONG",
        "shipping_branch_name": "PUDONG_ZHANGJIANG",
        "consignee_branch_code": "VWMS_4321"
    }
    logging.debug('Waybill no full big pen: {}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
    db.add(WaybillResp(package_id, json.dumps(ret)))
    return ret


def tb_create_waybill_missing_waybill_code(package_id, db):
    ret = {
        "short_address": "SHANGHAI",
        "trade_order_info": {
            "package_id": package_id
        },
        "waybill_code": '',
        "package_center_code": "VWMS_CENTER_CODE",
        "package_center_name": "微仓网络发运中心",
        "print_config": "VWMS_CONFIG",
        "shipping_branch_code": "VWMS_1234",
        "consignee_branch_name": "SHANGHAI_PUDONG",
        "shipping_branch_name": "PUDONG_ZHANGJIANG",
        "consignee_branch_code": "VWMS_4321"
    }
    logging.debug('Waybill No code: {}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
    db.add(WaybillResp(package_id, json.dumps(ret)))
    return ret


def tb_create_waybill_without_balance(*args):
    ret = {
        "error_response": {
            "code": 50,
            "msg": "Remote service error",
            "sub_code": "isv.invalid-parameter",
            "sub_msg": "电子面单余额不足"
        }
    }
    logging.debug('Waybill No Balance: {}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
    return ret


def tb_cancel_response_normal():
    return {
        "wlb_waybill_i_cancel_response": {
            "cancel_result": True
        }
    }


def tb_cancel_response_fail():
    return {
        "wlb_waybill_i_cancel_response": {
            "cancel_result": False
        }
    }


def tb_seller_get_response():
    return {
        "user_seller_get_response": {
            "user": {
                "user_id": 888888
            }
        }
    }


def tb_search_response_normal():
    return {
        "wlb_waybill_i_search_response": {
            "subscribtions": {
                "waybill_apply_subscription_info": [
                    {
                        "branch_account_cols": {
                            "waybill_branch_account": [
                                {
                                    "seller_id": 888888,
                                    "shipp_address_cols": {
                                        "waybill_address": [
                                            {
                                                "area": "朝阳区",
                                                "province": "北京",
                                                "town": "八里庄",
                                                "address_detail": "朝阳路高井，财满街，财经中心9号楼21单元6013",
                                                "city": "北京市",
                                                "waybill_address_id": 123
                                            }
                                        ]
                                    },
                                    "quantity": 123,
                                    "allocated_quantity": 123,
                                    "branch_code": "1321",
                                    "print_quantity": 32,
                                    "cancel_quantity": 10,
                                    "branch_name": "杭州余杭分部"
                                }
                            ]
                        },
                        "cp_type": 123,
                        "cp_code": "YTO"
                    }
                ]
            }
        }
    }
