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
