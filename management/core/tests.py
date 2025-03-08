from django.test import TestCase
from core.models import *
from rest_framework.test import APITestCase
from faker import Faker
faker = Faker()
from rest_framework import status
class Apitest(APITestCase):

    def setup():
        print('setup called')
    def test_register(self):
        _data = {
            "user": {
                    "username": "dummy_user",
                    "email": "dummy_user@example.com",
                    "password": "dummy_password"
                },
                "role": "abc"
            }    
        _response1 = self.client.post('/app/signup/', data=_data, format="json")
        # _sucess = _response1.json()
        self.assertEqual(_response1.status_code, status.HTTP_201_CREATED)

        _response2 = self.client.post('/app/signup/', data=_data, format="json")
        _error = _response2.json()
        self.assertEqual(_response2.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("user", _error)
        self.assertIn("username", _error["user"])
    
    def test_login(self):
        _data =     {
        "username": "admin",
        "password": "123"
        }

        response = self.client.post('/app/login/', data=_data, format='json')
        response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


