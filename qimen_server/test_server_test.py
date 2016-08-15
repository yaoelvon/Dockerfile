# -*- coding: utf-8 -*-
import hashlib
import os
import unittest
import urllib

from webtest import TestApp

from  test_server import app, v_url_decode


# sign签名算法, 返回奇门url
def qimen_sign(url, secret, method_args, xml_body):  # method_args为参数列表的dict
    request_args = {}
    url_head = url + "?"
    url_secret = secret
    url_str = '' + url_secret
    sign_list = []
    url_list = []
    request_args = method_args
    for key, value in request_args.items():
        sign_list.append(key + value)
        url_list.append(key + '=' + value.encode('UTF-8'))
    sign_list.sort()
    for item in sign_list:
        url_str += item
    url_str = url_str + xml_body + url_secret
    print "pre_md5_body: {0}".format(url_str)
    sign_md5 = hashlib.md5()
    sign_md5.update(url_str)
    # 签名生成，若仅需要签名，url生产部分可以忽略
    sign = sign_md5.hexdigest().upper()

    for item in url_list:
        url_head += '%s&' % (urllib.quote(item))
    # 最终url生成
    final_url = url_head + 'sign=' + sign
    print "url: {0}".format(final_url)

    return final_url


class TestServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['MODE'] = 'DEV_SQLITE'
        cls.test_client = TestApp(app)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        print "------set up finish------"

    def tearDown(self):
        print "------tear down finish------"

    # @unittest.skip('')
    def test_url_decode_success(self):
        url = 'format%3Dxml&timestamp%3D2016-05-04%2018%3A18%3A00&app_key%3Dtesterp_appkey&customerId%3Dc1458619373066&sign_method%3Dmd5&v%3D2.0&method%3Dtaobao.qimen.deliveryorder.confirm'
        d = v_url_decode(url)
        self.assertTrue(len(d) > 0)

    # @unittest.skip('')
    def test_set_response_param_success(self):
        xml_body = '<xml><result>success</result></xml>'
        r = self.test_client.post('/test_param', xml_body)
        self.assertEqual(r.status_code, 201)

    def test_reset_memory(self):
        r = self.test_client.post('/reset', '')
        self.assertTrue('no result' in r)

    # @unittest.skip('')
    def test_server_post_return_201(self):
        xml_body = '<xml><result>success</result></xml>'
        r = self.test_client.post('/test_param', xml_body)
        self.assertEqual(r.status_code, 201)

        url = '/qimen'
        secret = '1234'
        method_args = {
            'method': 'taobao.qimen.deliveryorder.confirm',
            # 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': '2016-05-04 18:18:00',
            'format': 'xml',
            'app_key': 'testerp_appkey',
            'v': '2.0',
            'sign_method': 'md5',
            'customerId': 'c1458619373066'
        }

        with open(r'./qimen_runguo1.xml', 'r') as f:
            xml_body = f.read()

        sign = qimen_sign(url, secret, method_args, xml_body)
        print "runguo1: {0}".format(sign)

        r = self.test_client.post(sign, xml_body)
        print dir(r)
        print type(r)
        self.assertEqual(r.status_code, 201)
        print 'body ======={0}'.format(r.normal_body)
        r.mustcontain('success')
        self.assertTrue('success' in r)

        r = self.test_client.get('/qimen')
        self.assertEqual(r.status_code, 200)
        print r.status
        print r.normal_body


if __name__ == '__main__':
    unittest.main()


