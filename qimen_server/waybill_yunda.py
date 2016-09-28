# coding: utf-8
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
import json
import uuid
import urllib
import base64
import bottle
import xmltodict
from bottle import HTTPError
from bottle.ext import sqlalchemy
from qimen_server.yunda_data import pdf_info
from qimen_server.database import Base, engine
from qimen_server.database import YunDaWaybillResp

yunda = bottle.Bottle(catchall=False)

plugin = sqlalchemy.Plugin(
    engine,  # SQLAlchemy engine created with create_engine function.
    Base.metadata,  # SQLAlchemy metadata, required only if create=True.
    keyword='db',  # Keyword used to inject session database in a route (default 'db').
    create=True,  # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
    commit=True,  # If it is true, plugin commit changessqlalchemy.plugin after route is executed (default True).
    use_kwargs=False
    # If it is true and keyword is not defined,
    # plugin uses **kwargs argument to inject session database (default False).
)

yunda.install(plugin)

@yunda.post('/cus_order/order_interface/<method>')
def handle_yunda_waybill(db, method):
    logging.debug('-------------HANDLE YUNDA WAYBILL REQUEST------------')
    q = dict(bottle.request.query)
    logging.debug('/cus_order/order_interface/: {0}'.format(method))
    logging.debug('query: {0}'.format(q))
    base_xml = q['xmldata']
    base64_xml =urllib.unquote(base_xml)
    logging.debug('xml_data {0}'.format(base64_xml))
    body = base64.b64decode(base64_xml)
    logging.debug(u'/cus_order/order_interface/: {0}'.format(body))
    body_dict = xmltodict.parse(body)
    orders = body_dict['orders']
    if method == 'interface_receive_order__mailno.php':
        response = make_yunda_response(db, method, orders)
    elif method == 'interface_cancel_order.php':
        response = make_yunda_response(db, method, orders)
    responses_dict = joint_xml_response(response)
    responses_xml = xmltodict.unparse(responses_dict)

    logging.debug('method={0} rsps={1}'.format(method, responses_xml))
    return responses_xml

def make_yunda_response(db, method, orders):
    GET_MAPPING = {
        '0': yunda_create_waybill_normal,
        '1': yunda_create_waybill_missing_all_info,
    }
    CANCEL_MAPPING = {
        '0': yunda_cancel_response_normal,
        '8': yunda_cancel_response_fail
    }
    YUNDA_ROUTE_MAP = {
        'interface_receive_order__mailno.php': GET_MAPPING,
        'interface_cancel_order.php': CANCEL_MAPPING
    }
    if isinstance(orders['order'], dict):
        order_code = orders['order']['order_serial_no']
        logging.debug('yunda reg order code {0}'.format(order_code))
        func = YUNDA_ROUTE_MAP.get(method).get(order_code[-3])
        response =func(db, order_code)
        logging.debug('yunda method {0} respones {1}'.format(method, response))
        return response
    elif isinstance(orders['order'], list):
        order_codes = [order['order_serial_no'] for order in orders['order']]
        logging.debug('yunda reg order codes {0}'.format(order_codes))
        response = [YUNDA_ROUTE_MAP.get(method).get(order_code[-3])(db, order_code) for order_code in order_codes]
        logging.debug('yunda method {0} respones {1}'.format(method, response))
        return response

@yunda.get('/waybill')
def yunda_waybill(db):
    logging.debug('-------------GET YUNDA WAYBILL-------------')
    q = dict(bottle.request.query)
    logging.debug(q)
    logging.debug(bottle.request.body.getvalue().decode('utf-8'))
    order_code = q.get('order_code')
    record = db.query(YunDaWaybillResp).filter_by(order_id=order_code).first()
    if record:
        return record.body
    else:
        return HTTPError(404, None)


@yunda.post('/reset')
def yunda_reset(db):
    [db.delete(item) for item in db.query(YunDaWaybillResp).all()]


def joint_xml_response(response):
    return {
        'responses': {
           'response': response
        }
    }

def yunda_create_waybill_normal(db, order_code):
    waybill_code = str(uuid.uuid4()).split('-')[-1]
    rsp = {
            'order_serial_no': order_code,
            'mail_no': waybill_code,
            'pdf_info': json.dumps(pdf_info),
            'status': 1,
            'msg': 'success'
    }
    logging.debug('YunDa Waybill normal: {0}'.format(json.dumps(rsp)))
    db.add(YunDaWaybillResp(order_code, json.dumps(rsp)))
    return rsp


def yunda_create_waybill_missing_all_info(db, order_code):
    waybill_code = str(uuid.uuid4()).split('-')[-1]
    rsp = {
            'order_serial_no': order_code,
            'mail_no': waybill_code,
            'pdf_info': None,
            'status': 0,
            'msg': 'failed'
    }
    logging.debug('YunDa Waybill normal: {}'.format(json.dumps(rsp, indent=4, ensure_ascii=False)))
    db.add(YunDaWaybillResp(order_code, json.dumps(rsp)))
    return rsp


def yunda_cancel_response_normal(db, order_code):
    rsp = {
        'order_serial_no': order_code,
        'status': 1,
        'msg': True,
    }
    return rsp


def yunda_cancel_response_fail(db, order_code):
    rsp = {
        'order_serial_no': order_code,
        'status': 0,
        'msg': False
    }
    return rsp

