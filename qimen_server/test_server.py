import json
import logging
import os
import xmltodict
from bottle.ext import sqlalchemy


import bottle
from JsonUtil import get_dict_value
from bottle import HTTPError
from database import Base, engine, Req, Resp

from waybill_yto import yto
from waybill_jd import jd
from waybill_yunda import yunda
from waybill_sf import sf
from waybill_tb import tb, handle_taobao_waybill

logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(message)s', level=logging.DEBUG)

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


@app.get('/v2/qimen')
def show_qimen(db):
    records = db.query(Req).all()
    _requests = [xmltodict.parse(e.body).get('request') for e in records]

    q = bottle.request.query
    for pattern in q.keys():
        _requests = [e for e in _requests if get_dict_value(pattern, e) == q.get(pattern)]

    if _requests:
        logging.info('GET /v2/qimen: {}'.format(_requests[-1]))
        return json.dumps(_requests[-1])
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
        return xmltodict.unparse(_bodies[-1], pretty=True)


def get_xml_response(db):
    rsp = db.query(Resp).order_by(Resp.id.desc()).first()
    if rsp:
        return rsp.body
    else:
        with open(os.path.join(base_dir + '/qimen_rsp.xml')) as f:
            return f.read()


@app.post('/router/rest')
def taobao_waybill_request(db):
    return handle_taobao_waybill(db)


@app.post('/reset')
def post(db):
    [db.delete(item) for item in db.query(Req).all()]
    [db.delete(item) for item in db.query(Resp).all()]


@app.post('/set_qimen_response')
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

    entity = Req(bottle.request.body.getvalue().decode('utf-8'))
    db.add(entity)
    return get_xml_response(db)


app.mount('yto', yto)
app.mount('tb', tb)
app.mount('jd', jd)
app.mount('yunda', yunda)
app.mount('sf', sf)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
