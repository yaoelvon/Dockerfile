# coding: utf-8
import rpyc
from rpyc.utils.server import ThreadedServer  # or ForkingServer


class TestParamService(rpyc.Service):
    def exposed_set_response_message(self, body):
        rsp = Rsp(body)
        db.add(rsp)
        db.commit()
        return True

    def exposed_get_request_message(self, req_type):
        entity = db.query(Entity).first()
        if entity:
            return entity.name
        return None


if __name__ == '__main__':
    server = ThreadedServer(TestParamService, port=12345)
    server.start()


def test_set_response_param_success(self):
    conn = rpyc.connect("localhost", 12345)
    x = conn.root.set_response_message('<xml><result>success</result></xml>')
    assert x == True
