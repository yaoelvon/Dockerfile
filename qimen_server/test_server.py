import json
import logging
import os
import urllib

import xmltodict
import waybill
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base

import bottle
from JsonUtil import get_dict_value
from bottle import HTTPError

logging.basicConfig(format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                    level=logging.DEBUG)
Base = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=True)

app = bottle.Bottle(catchall=False)
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

app.install(plugin)
base_dir = os.path.abspath(os.path.dirname(__file__))


class Req(Base):
    __tablename__ = 'request'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    body = Column(String(10000))

    def __init__(self, req_body):
        self.body = req_body

    def __repr__(self):
        return "<Req('%d', '%s')>" % (self.id, self.body)


class Resp(Base):
    __tablename__ = 'response'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    body = Column(String(10000))

    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return "<Req('%d', '%s')>" % (self.id, self.body)


class WaybillResp(Base):
    __tablename__ = 'waybill_response'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    key = Column(String(36))
    body = Column(String(10000))

    def __init__(self, key, body):
        self.key = key
        self.body = body

    def __repr__(self):
        return "<WaybillResp('%d', '%s', '%s')>" % (self.id, self.key, self.body)


@app.get('/qimen')
def show(db):
    req = db.query(Req).first()

    if req:
        # return entities
        return json.dumps(xmltodict.parse(req.body).get('request'))
    return HTTPError(404, None)


@app.get('/v2/qimen')
def show_qimen(db):
    records = db.query(Req).all()
    _requests = [xmltodict.parse(e.body).get('request') for e in records]

    q = bottle.request.query
    for pattern in q.keys():
        _requests = [e for e in _requests if get_dict_value(pattern, e) == q.get(pattern)]

    if _requests:
        logging.info('GET /v2/qimen: {}'.format(_requests[0]))
        return json.dumps(_requests[0])
    return HTTPError(404, None)


@app.get('/v2/qimen_confirm')
def show_qimen_confirm(db):
    ret = dict()
    ret['req'] = get_xml_request(db)
    ret['rsp'] = get_xml_response(db)
    logging.debug('GET /v2/qimen_confirm: {}'.format(ret))
    return json.dumps(ret)


def get_xml_request(db):
    records = db.query(Req).all()
    _bodies = [xmltodict.parse(e.body) for e in records]
    q = bottle.request.query
    logging.info('before filter bodies: {}'.format(_bodies))
    logging.info('query: {}'.format(dict(q)))
    for pattern in q.keys():
        _bodies = [e for e in _bodies
                   if get_dict_value(pattern, e.get('request')) == q.get(pattern)]
    if _bodies:
        logging.info('after filter bodies: {}'.format(_bodies))
        return xmltodict.unparse(_bodies[0], pretty=True)


def get_xml_response(db):
    rsp = db.query(Resp).order_by(Resp.id.desc()).first()
    if rsp:
        return rsp.body
    else:
        with open(os.path.join(base_dir + '/qimen_rsp.xml')) as f:
            return f.read()


@app.post('/reset')
def post(db):
    [db.delete(item) for item in db.query(Req).all()]
    [db.delete(item) for item in db.query(Resp).all()]


@app.post('/test_param')
def post(db):
    bottle.response.status = '201 Created'
    bottle.response.content_type = 'application/xml'

    rsp = Resp(bottle.request.body.getvalue())
    db.add(rsp)


@app.post('/qimen')
def post(db):
    logging.info('POST /qimen REQ_BODY: {}'.format(bottle.request.body.getvalue()))

    bottle.response.status = '201 Created'
    bottle.response.content_type = 'application/xml'

    # save request
    entity = Req(bottle.request.body.getvalue().decode('utf-8'))
    db.add(entity)

    # response
    return get_xml_response(db)


@app.post('/waybill_yto')
def post():
    if waybill.YTO == 0:
        ret = waybill.yto_response()
    elif waybill.YTO == 1:
        ret = waybill.yto_response_missing_1()
    else:
        ret = waybill.yto_response_missing_2()
    return ret


@app.post('/waybill_yto/setting')
def post():
    body = bottle.request.body.getvalue()
    logging.info("/waybill_yto/setting BODY {}".format(body))
    yto = json.loads(body).get('YTO')
    if yto:
        waybill.YTO = int(yto)
    else:
        waybill.YTO = 0
    return json.dumps({'state': 'success'})


@app.post('/router/rest')
def taobao_waybill(db):
    q = dict(bottle.request.query)
    logging.debug(q)
    body = bottle.request.body.getvalue()
    logging.debug(body)

    method = q['method']
    if method == 'taobao.wlb.waybill.i.get':
        body_request = body[body.find("=") + 1:]
        request_data = urllib.unquote(body_request).replace("+", " ")
        print 'request_data', request_data
        package_id = json.loads(request_data)['trade_order_info_cols'][0]['package_id']
        express_company = json.loads(request_data)['cp_code']
        print "package_id", package_id
        return handle_waybill_get(db, package_id, express_company)
    elif method == 'taobao.wlb.waybill.i.candel':
        return handle_waybill_cancel(db)
    elif method == 'taobao.wlb.waybill.i.search':
        return handle_waybill_address(db)


def handle_waybill_cancel(db):
    return json.dumps(waybill.wlb_waybill_i_cancel_response())


def handle_waybill_address(db):
    return json.dumps(waybill.wlb_waybill_i_search_response())


def handle_waybill_get(db, package_id, express_company):
    key, rsp = waybill.wlb_waybill_i_get_response(package_id, express_company)
    dumped_rsp = json.dumps(rsp)
    db.add(WaybillResp(key, dumped_rsp))
    return dumped_rsp


@app.get('/waybill')
def taobao_waybill(db):
    q = dict(bottle.request.query)
    logging.debug(q)
    logging.debug(bottle.request.body.getvalue().decode('utf-8'))
    waybill_code = q.get('waybill_code')
    record = db.query(WaybillResp).filter_by(key=waybill_code).first()
    if record:
        return record.body
    else:
        return HTTPError(404, None)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
