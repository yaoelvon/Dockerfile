# coding: utf-8
import logging
import uuid
import json
import xmltodict
import bottle
import urllib
from bottle import HTTPError
from bottle.ext import sqlalchemy
from qimen_server.database import Base, engine
from qimen_server.database import YtoWaybillReq, YtoWaybillResp

yto = bottle.Bottle(catchall=False)

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

yto.install(plugin)


@yto.post('/waybill_yto')
def yto_waybill(db):
    RESPONSE_MAPPING = {
        '0': yto_response_normal,
        '1': yto_response_no_part_big_pen,
        '2': yto_response_no_all_big_pen,
        '3': yto_response_no_waybill_code
    }
    query_url = dict(bottle.request.query)
    logging.debug('query_url: {}'.format(json.dumps(query_url, ensure_ascii=False, indent=4)))
    query_url['logistics_interface'] = urllib.unquote(query_url['logistics_interface'])
    logging.debug('logistics_interface: {}'.format(query_url['logistics_interface']))

    db.add(YtoWaybillReq(json.dumps(query_url)))

    xml_req = xmltodict.parse(query_url['logistics_interface'], encoding='utf-8')
    logging.debug('yto_waybill xml req: {}'.format(json.dumps(xml_req)))
    rsp_func = RESPONSE_MAPPING.get(xml_req['RequestOrder']['txLogisticID'][-3]) or yto_response_normal

    yto_code, yto_rsp = rsp_func()
    logging.debug('YTO response: {} {}'.format(yto_code, yto_rsp))
    db.add(YtoWaybillResp(yto_code, yto_rsp.decode('utf-8')))

    return yto_rsp


@yto.get('/v1/waybill_yto')
def yto_waybill(db):
    yto_rsp = db.query(YtoWaybillResp).order_by(YtoWaybillResp.id.desc()).first()
    # yto_rsp = db.query(YtoWaybillResp).first()
    if yto_rsp:
        # return entities
        rsp = json.dumps(xmltodict.parse(yto_rsp.body).get('Response'))
        print '--yto--body{0}'.format(json.loads(rsp))
        return rsp
    return HTTPError(404, None)


@yto.post('/reset')
def yto_reset(db):
    [db.delete(item) for item in db.query(YtoWaybillReq).all()]
    [db.delete(item) for item in db.query(YtoWaybillResp).all()]

@yto.get('/waybill_yto_search')
def yto_waybill_search(db):
    query_url = dict(bottle.request.query)
    logging.debug(query_url)
    waybill_code = query_url.get('waybill_code')
    yto_rsp = db.query(YtoWaybillResp).filter_by(yto_code=waybill_code).first()
    if yto_rsp:
        logging.debug('yto_waybill_search Response: {}'.format(yto_rsp.body))
        return yto_rsp.body
    return HTTPError(404, None)


def yto_response_normal():
    code = str(uuid.uuid4()).split('-')[-1]
    return code, '''<Response>
    <logisticProviderID>YTO</logisticProviderID>
    <txLogisticID>WP15183117908113</txLogisticID>
    <clientID>K21000119</clientID>
    <mailNo>{0}</mailNo>
    <distributeInfo>
        <shortAddress>300-006-000</shortAddress>
        <consigneeBranchCode>210185</consigneeBranchCode>
        <packageCenterCode>210901</packageCenterCode>
        <packageCenterName>上海转运中心</packageCenterName>
    </distributeInfo><code>200</code>
    <success>true</success>
</Response>'''.format(code)


def yto_response_no_part_big_pen():
    code = str(uuid.uuid4()).split('-')[-1]
    return code, '''<Response>
    <logisticProviderID>YTO</logisticProviderID>
    <txLogisticID>WP15183117908113</txLogisticID>
    <clientID>K21000119</clientID>
    <mailNo>{}</mailNo>
    <distributeInfo>
        <shortAddress>300-006 000</shortAddress>
        <consigneeBranchCode></consigneeBranchCode>
        <packageCenterCode></packageCenterCode>
        <packageCenterName></packageCenterName>
    </distributeInfo><code>200</code>
    <success>true</success>
</Response>'''.format(code)


def yto_response_no_all_big_pen():
    code = str(uuid.uuid4()).split('-')[-1]
    return code, '''<Response>
    <logisticProviderID>YTO</logisticProviderID>
    <txLogisticID>WP15183117908113</txLogisticID>
    <clientID>K21000119</clientID>
    <mailNo>{}</mailNo>
    <distributeInfo>
        <shortAddress></shortAddress>
        <consigneeBranchCode></consigneeBranchCode>
        <packageCenterCode></packageCenterCode>
        <packageCenterName></packageCenterName>
    </distributeInfo><code>200</code>
    <success>true</success>
</Response>'''.format(code)


def yto_response_no_waybill_code():
    code = str(uuid.uuid4()).split('-')[-1]
    return code, '''<Response>
    <logisticProviderID>YTO</logisticProviderID>
    <txLogisticID>WP15183117908113</txLogisticID>
    <clientID>K21000119</clientID>
    <mailNo></mailNo>
    <distributeInfo>
        <shortAddress>300-006-000</shortAddress>
        <consigneeBranchCode>210185</consigneeBranchCode>
        <packageCenterCode>210901</packageCenterCode>
        <packageCenterName>上海转运中心</packageCenterName>
    </distributeInfo><code>200</code>
    <success>true</success>
</Response>'''
