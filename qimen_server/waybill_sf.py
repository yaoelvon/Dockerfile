# coding: utf-8
from __future__ import unicode_literals
import logging
import uuid
import json
import bottle
import requests
from bottle import HTTPError
from bottle.ext import sqlalchemy
from database import Base, engine
from database import SfToken
from database import SfWaybillResp
from database import SfOrderWaybillResp

# SF_CALLBACK_URL = os.environ.get('SF_CALLBACK_URL')

sf = bottle.Bottle(catchall=False)

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

sf.install(plugin)


@sf.post('/public/v1.0/security/access_token/sf_appid/<sf_appid>/sf_appkey/<sf_appkey>')
def sf_create_accedss_token(sf_appid, sf_appkey, db):
    logging.debug('-------- SHUNFENG WAYBILL REG ACCESS TOKEN-----------')
    body = bottle.request.body.getvalue()
    json_request = json.loads(body)
    logging.debug('/security/access_token/ : {}'.format(json.dumps(json_request, indent=4, ensure_ascii=False)))
    trans_message_id = json_request['head']['transMessageId']
    token = sf_reg_access_token(trans_message_id, db)
    return json.dumps(token)


@sf.post('/public/v1.0/security/query/access_token/sf_appid/<sf_appid>/sf_appkey/<sf_appkey>')
def sf_query_access_token(sf_appid, sf_appkey, db):
    logging.debug('--------SHUNFENG WAYBILL GET ACCESS TOKEN-----------')
    body = bottle.request.body.getvalue()
    json_request = json.loads(body)
    logging.debug('/security/query/access_token/ : {}'.format(json.dumps(json_request, indent=4, ensure_ascii=False)))
    trans_message_id = json_request['head']['transMessageId']
    query_token = sf_get_access_token(trans_message_id, db)
    return json.dumps(query_token)


@sf.post('/public/v1.0/security/query/access_token/sf_appid/<sf_appid>/sf_appkey/<sf_appkey>')
def sf_refresh_token(sf_appid, sf_appkey, db):
    logging.debug('--------SHUNFENG WAYBILL REFRESH ACCESS TOKEN---------')
    body = bottle.request.body.getvalue()
    json_ = json.loads(body)
    logging.debug('/security/refresh_token/access_token/ : {}'.format(json.dumps(json_, indent=4, ensure_ascii=False)))
    trans_message_id = json_['head']['transMessageId']
    again_refresh = sf_refresh_access_token(trans_message_id, db)
    return json.dumps(again_refresh)


@sf.post('/rest/v1.0/order/access_token/<access_token>/sf_appid/<sf_appid>/sf_appkey/<sf_appkey>')
def handle_sf_waybill(access_token, sf_appid, sf_appkey, db):
    logging.debug('-------------HANDLE SHUNFENG WAYBILL GET-------------')
    GET_MAPPING = {
        '0': sf_reg_order_waybill_normal,
    }
    body = bottle.request.body.getvalue()
    json_request = json.loads(body)
    logging.debug('/router/rest json request: {}'.format(json.dumps(json_request, indent=4, ensure_ascii=False)))
    trans_message_id = json_request['head']['transMessageId']
    order_id = json_request['body']['orderId']
    func = GET_MAPPING.get(order_id[-3]) or sf_reg_order_waybill_normal
    generate_order = func(trans_message_id, order_id, db)
    # callback client normal information
    success_waybill = sf_normal_rsp(trans_message_id, order_id, db)
    SF_CALLBAC_URL = 'http://localhost:5000/waybill_push/shunfeng'
    requests.post(SF_CALLBAC_URL, json.dumps(success_waybill))
    return json.dumps(generate_order)


@sf.post('/public/v1.0/order/query/access_token/<access_token>/sf_appid/<sf_appid>/sf_appkey/<sf_appkey>')
def query_waybill(access_token, sf_appid, sf_appkey, db):
    logging.debug('-------------HANDLE SHUNFENG WAYBILL QUERY RESULT-------------')
    GET_MAPPING = {
        '0': sf_query_waybill_normal,
    }
    body = bottle.request.body.getvalue()
    json_request = json.loads(body)
    logging.debug('/router/rest json request: {}'.format(json.dumps(json_request, indent=4, ensure_ascii=False)))
    trans_message_id = json_request['head']['transMessageId']
    order_id = json_request['body']['orderId']
    func = GET_MAPPING.get(order_id[-3]) or sf_query_waybill_normal
    success_order = func(trans_message_id, order_id, db)
    return json.dumps(success_order)


@sf.get('/waybill')
def taobao_waybill(db):
    logging.debug('-------------GET SF WAYBILL-------------')
    q = dict(bottle.request.query)
    logging.debug(q)
    logging.debug(bottle.request.body.getvalue().decode('utf-8'))
    order_code = q.get('order_code')
    record = db.query(SfWaybillResp).filter_by(key=order_code).first()
    if record:
        return record.body
    else:
        return HTTPError(404, None)


@sf.post('/reset')
def sf_reset(db):
    [db.delete(item) for item in db.query(SfOrderWaybillResp).all()]
    [db.delete(item) for item in db.query(SfWaybillResp).all()]
    [db.delete(item) for item in db.query(SfToken).all()]


def sf_reg_access_token(trans_message_id, db):
    token = db.query(SfToken).filter_by(trans_message_id=trans_message_id).first()
    access_token = str(uuid.uuid4())
    refresh_token = str(uuid.uuid4())
    if not token:
        db.add(SfToken(trans_message_id, access_token, refresh_token))
    else:
        access_token = token.access_token
        refresh_token = token.refresh_token
    ret = {
    "head": {
        "transType": "4301",
        "transMessageId": trans_message_id,
        "code": "EX_CODE_OPENAPI_0200",
        "message": u"申请 ACCESS TOKEN 成功",
        },
    "body": {
        "accessToken": access_token,
        "refreshToken": refresh_token
        }
    }
    logging.debug('SF Token reg : {0}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
    return ret

def sf_refresh_access_token(trans_message_id, db):
    record = db.query(SfToken).filter_by(trans_message_id=trans_message_id).first()
    refresh_token = str(uuid.uuid4())
    ret = {
    "head": {
        "transType":"4302",
        "transMessageId": "201404120000000001",
        "code": "EX_CODE_OPENAPI_0200",
        "message": "刷新 ACCESS TOKEN 成功"
    },
        "body": {
            "accessToken": "094CC6A09D9B9E8FEF6AE5499158A678",
            "refreshToken":refresh_token
        }
    }
    record.refresh_token = refresh_token
    logging.debug('SFToken Refreash {0}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
    return ret

def sf_get_access_token(trans_message_id, db):
    record = db.query(SfToken).filter_by(trans_message_id=trans_message_id).first()
    ret = {
    "head": {
        "transType":"4300",
        "transMessageId": "201404120000000001",
        "code": "EX_CODE_OPENAPI_0200",
        "message": u"查询 ACCESS_TOKEN 成功",
    },
    "body": {
        "accessToken": record.access_token,
        "refreshToken": record.refresh_token
    }
    }
    logging.debug('SFToken Get {0}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
    return ret


def sf_reg_order_waybill_normal(trans_message_id, order_id, db):
    ret = {
    "head": {
        "transType": 4200,
        "transMessageId": trans_message_id,
        "code": "EX_CODE_OPENAPI_0200",
        "message": "操作成功"
        },
    "body": {
        "orderId": order_id,
        "filterLevel": "4",
        "orderTriggerCondition": "1"
        }
    }
    logging.debug('SFWaybill reg normal: {}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
    db.add(SfOrderWaybillResp(order_id, trans_message_id, json.dumps(ret)))
    return ret


def sf_normal_rsp(trans_message_id, order_id, db):
    waybill_code = str(uuid.uuid4()).split('-')[-1]
    ret = {
    "head": {
        "transType": "4203",
        "transMessageId": trans_message_id,
        "code": " EX_CODE_OPENAPI_0200 ",
    },
    "body": {
        "orderId": order_id,
        "mailNo": waybill_code,
        "origincode": "010",
        "destcode": "755",
        "filterResult": "2"
    }
    }
    logging.debug('SFWaybill normal: {}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
    db.add(SfWaybillResp(trans_message_id, order_id, json.dumps(ret)))
    return ret


def sf_query_waybill_normal(trans_message_id, order_id, db):
    record = db.query(SfWaybillResp).filter_by(order_id=order_id).first()
    rsp = json.loads(record.body)
    rsp['head']['meassage'] = u'订单查询成功'
    return rsp


# def sf_create_waybill_missing_part_big_pen(order_id, db):
#     return ret
#
#
# def sf_create_waybill_missing_full_big_pen(order_id, db):
#     waybill_code = str(uuid.uuid4()).split('-')[-1]
#     ret = {
#         "short_address": "",
#         "trade_order_info": {
#             "order_id": order_id
#         },
#         "waybill_code": waybill_code,
#         "package_center_code": "",
#         "package_center_name": "",
#         "print_config": "VWMS_CONFIG",
#         "shipping_branch_code": "VWMS_1234",
#         "consignee_branch_name": "SHANGHAI_PUDONG",
#         "shipping_branch_name": "PUDONG_ZHANGJIANG",
#         "consignee_branch_code": "VWMS_4321"
#     }
#     logging.debug('Waybill no full big pen: {}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
#     db.add(WaybillResp(order_id, json.dumps(ret)))
#     return ret
#
#
# def sf_create_waybill_missing_waybill_code(order_id, db):
#     ret = {
#         "short_address": "SHANGHAI",
#         "trade_order_info": {
#             "order_id": order_id
#         },
#         "waybill_code": '',
#         "package_center_code": "VWMS_CENTER_CODE",
#         "package_center_name": "微仓网络发运中心",
#         "print_config": "VWMS_CONFIG",
#         "shipping_branch_code": "VWMS_1234",
#         "consignee_branch_name": "SHANGHAI_PUDONG",
#         "shipping_branch_name": "PUDONG_ZHANGJIANG",
#         "consignee_branch_code": "VWMS_4321"
#     }
#     logging.debug('Waybill No code: {}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
#     db.add(WaybillResp(order_id, json.dumps(ret)))
#     return ret
#
#
# def sf_create_waybill_without_balance(*args):
#     ret = {
#         "error_response": {
#             "code": 50,
#             "msg": "Remote service error",
#             "sub_code": "isv.invalid-parameter",
#             "sub_msg": "电子面单余额不足"
#         }
#     }
#     logging.debug('Waybill No Balance: {}'.format(json.dumps(ret, indent=4, ensure_ascii=False)))
#     return ret
#
#
# def sf_cancel_response_normal():
#     return {
#         "wlb_waybill_i_cancel_response": {
#             "cancel_result": True
#         }
#     }
#
#
# def sf_cancel_response_fail():
#     return {
#         "wlb_waybill_i_cancel_response": {
#             "cancel_result": False
#         }
#     }
#
#
# def sf_seller_get_response():
#     return {
#         "user_seller_get_response": {
#             "user": {
#                 "user_id": 888888
#             }
#         }
#     }
#
#
def sf_request_message():
    return {
        "head": {
            "transMessageId": "201404120000000001",
            "transType": "200"
        },
        "body": {
            "orderId": "OPEN123456789",
            "expressType": 1,
            "isDoCall": 2,
            "needReturnTrackingNo": 1,
            "payMethod": "1",
            "remark": "易碎物品，小心轻放",
            "sendStartTime": "2014-08-26 07:31:55",
            "custId": "7550010173",
            "cargoInfo": {
            "cargo": "iphone5s",
            "cargoAmount": "4999.00",
            "cargoCount": "4",
            "cargoTotalWeight": "0.8",
            "cargoUnit": "部",
            "cargoWeight": "0.15",
            "parcelQuantity": 1
        },
        "consigneeInfo": {
            "address": "南山区深圳软件产业基地",
            "city": "深圳市",
            "company": "顺丰科技",
            "contact": "黄飞鸿",
            "mobile": "18588416666",
            "province": "广东省",
            "shipperCode": "518052",
            "tel": "0755-33916666"
        },
        "deliverInfo": {
            "address": "沧浪区人民路沧浪亭街 31 号神罗科技大厦",
            "city": "苏州市",
            "company": "神罗科技",
            "contact": "莫桂兰",
            "mobile": "13612822250",
            "province": "江苏省",
            "shipperCode ": "215000",
            "tel": "010-95127777"
        },
        "addedServices": [
            {
                "name": "COD",
                "value": "19996"
            }
            ]
        }
    }

