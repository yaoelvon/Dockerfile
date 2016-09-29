# coding: utf-8
import logging
import uuid
import json
import xmltodict
import bottle
from bottle import HTTPError
from bottle.ext import sqlalchemy
from database import Base, engine
from database import JdWaybillSendResp, JdWaybillApplyResp

jd = bottle.Bottle(catchall=False)

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

jd.install(plugin)


@jd.get('/routerjson')
def apply_jd_waybill(db):
    query = bottle.request.query
    if query['method'] == 'jingdong.etms.waybillcode.get':
        jd_code, resp = jd_get_response_normal()
        logging.debug('JD response: {} {}'.format(jd_code, resp))
        db.add(JdWaybillApplyResp(jd_code, resp))
    else:  # '''jingdong.etms.waybillcode.send'''
        jd_param = json.loads(query['360buy_param_json'])
        delivery_id = jd_param['deliveryId']
        order_id = jd_param['orderId']
        resp = jd_send_response_normal(delivery_id, order_id)
        db.add(JdWaybillSendResp(delivery_id, order_id, resp))
        logging.debug('JD response: {}'.format(resp))

    return resp


@jd.get('/jd_waybill')
def jd_waybill(db):
    query = bottle.request.query
    jd_rsp = db.query(JdWaybillSendResp).filter_by(wms_order_code=query.get('wms_order_code')).first()
    if jd_rsp:
        # return entities
        return jd_rsp.body
    return HTTPError(404, None)


def jd_get_response_normal():
    code = str(uuid.uuid4()).split('-')[-1]
    return code, json.dumps({
        'jingdong_etms_waybillcode_get_responce':
            {'resultInfo':
                 {'message': u'成功',
                  'code': 100,
                  'deliveryIdList': [code]
                  },
             'code': u'0'
             }
    })


def jd_send_response_normal(deliver_id, order_id):
    return json.dumps({
        "jingdong_etms_waybill_send_responce": {
            "resultInfo": {
                "message": u"成功",
                "deliveryId": deliver_id,
                "code": 100,
                "orderId": order_id
            }
        }
    })
