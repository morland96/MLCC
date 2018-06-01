import json
import logging
import unittest

import mlcc.run as run

logging.basicConfig(
    level=logging.DEBUG,
    format='%(filename)s [%(levelname)s] %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)
logger = logging.getLogger("test")

base_url = "http://127.0.0.1:5000/"

json_header = {"Content-Type": 'application/json'}
admin_json_header = {"Content-Type": 'application/json'}


class TestUserAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logger = logger
        run.app.config['TESTING'] = True
        cls.app = run.app.test_client()
        r = cls.app.delete("/api/users/_test")
        cls.logger.debug("\ndelete _test account with %s " % r.status_code)

    def test_step1_register(self):
        r = self.app.post(
            "/api/users",
            headers=json_header,
            data='{"username": "_test", "password": "password"}')
        self.assertEqual(r.status_code, 201)
        data = json.loads(r.data)
        self.assertEqual(data['username'], "_test")
        self.logger.debug(data)

    def test_step2_login(self):
        r = self.app.post(
            "/api/sessions",
            headers=json_header,
            data='{"username": "_test", "password": "password"}')
        data = json.loads(r.data)
        self.assertEqual(r.status_code, 201)
        json_header['Authentication-Token'] = data['token']
        self.assertIsNotNone(data['token'])
        self.logger.debug("Get a token : %s" % data['token'])
        self.logger.debug(data)

    def test_step3_token(self):
        r = self.app.post("/api/test/token", headers=json_header)
        self.assertEqual(r.status_code, 201)
        self.logger.debug(r.data)

    def test_step4_update_user(self):
        r = self.app.put(
            "/api/users/_test", headers=json_header, data='{"password":"111"}')
        self.assertEqual(r.status_code, 201)
        self.logger.debug(r.data)
        r = self.app.post(
            "/api/sessions",
            headers=json_header,
            data='{"username": "_test", "password": "111"}')
        self.assertEqual(r.status_code, 201)

    def test_step5_delete_user(self):
        r = self.app.delete("/api/users/_test", headers=json_header, data='{}')
        self.assertEqual(r.status_code, 204)