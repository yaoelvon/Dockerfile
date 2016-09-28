from sqlalchemy import create_engine, Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=True)


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


class YtoWaybillReq(Base):
    __tablename__ = 'ytowaybill_request'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    url_params = Column(String(10000))

    def __init__(self, url_params):
        self.url_params = url_params

    def __repr__(self):
        return "<YtoWaybillReq('%d', '%s')>" % (self.id, self.url_params)


class YtoWaybillResp(Base):
    __tablename__ = 'ytowaybill_response'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    yto_code = Column(String(36))
    body = Column(String(10000))

    def __init__(self, yto_code, body):
        self.yto_code = yto_code
        self.body = body

    def __repr__(self):
        return "<YtoWaybillResp('%d', '%s', '%s')>" % (self.id, self.yto_code, self.body)


class JdWaybillApplyResp(Base):
    __tablename__ = 'jdwaybill_apply_response'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    jd_code = Column(String(36))
    body = Column(String(10000))

    def __init__(self, jd_code, body):
        self.jd_code = jd_code
        self.body = body

    def __repr__(self):
        return "<JDWaybillApplyResp('%d', '%s', '%s')>" % (self.id, self.jd_code, self.body)


class JdWaybillSendResp(Base):
    __tablename__ = 'jdwaybill_send_response'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    jd_code = Column(String(36))
    wms_order_code = Column(String(50))
    body = Column(String(10000))

    def __init__(self, jd_code, wms_order_code, body):
        self.jd_code = jd_code
        self.wms_order_code = wms_order_code
        self.body = body

    def __repr__(self):
        return "<JDWaybillSendResp('%d', '%s', '%s')>" % (self.id, self.jd_code, self.body)


class YunDaWaybillResp(Base):
    __tablename__ = 'yunda_waybill_response'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    order_id = Column(String(36))
    body = Column(String(10000))

    def __init__(self, order_id, body):
        self.order_id = order_id
        self.body = body

    def __repr__(self):
        return "<YundaWaybillResp('%d', '%s', '%s')>" % (self.id, self.order_id, self.body)


class SfOrderWaybillResp(Base):
    __tablename__ = 'sf_order_waybill_response'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    order_id = Column(String(36))
    trans_message_id = Column(String(36))
    body = Column(String(10000))

    def __init__(self, trans_message_id, order_id, body):
        self.order_id = order_id
        self.trans_message_id = trans_message_id
        self.body = body

    def __repr__(self):
        return "<SFWaybillResp('%d','%s', '%s', '%s')>" % (self.id, self.order_id, self.trans_message_id, self.body)

class SfWaybillResp(Base):
    __tablename__ = 'sf_query_waybill_response'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    order_id = Column(String(36))
    trans_message_id = Column(String(36))
    body = Column(String(10000))

    def __init__(self, trans_message_id, order_id, body):
        self.order_id = order_id
        self.trans_message_id = trans_message_id
        self.body = body

    def __repr__(self):
        return "<SFQueryWaybillResp('%d','%s', '%s', '%s')>" % (self.id, self.order_id, self.trans_message_id, self.body)

class SfToken(Base):
    __tablename__ = 'sf_token'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    trans_message_id = Column(String(36))
    access_token = Column(String(100))
    refresh_token = Column(String(100))

    def __init__(self, trans_message_id, access_token, refresh_token):
        self.trans_message_id = trans_message_id
        self.access_token = access_token
        self.refresh_token = refresh_token

    def __repr__(self):
        return "<SfToken('%d','%s', '%s', '%s')>" % (self.id, self.trans_message_id, self.access_token, self.refresh_token)
