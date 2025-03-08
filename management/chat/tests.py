from rest_framework.test import APITestCase
from core.models import *
from rest_framework import status

class ApiTest(APITestCase):
    fixtures= ['main.json']
    def setup():
        print('setup called')
    # api/chat/view
    def test_get_chat_history(self):
        _response = self.client.get('/api/chat/view', format='json')
        _data = _response.json()
        print(_data)
        self.assertEqual(_response.status_code,status.HTTP_200_OK)
