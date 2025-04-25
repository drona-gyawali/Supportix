# from rest_framework.test import APITestCase
# from django.contrib.auth.models import User
# from rest_framework import status

# class ApiTest(APITestCase):
#     fixtures = ['main.json']

#     def setUp(self):
#         self.user = User.objects.create_user(username="admin", password="admin123")
#         self.client.login(username="admin", password="admin123")

#     def test_get_chat_history(self):
#         response = self.client.get('/api/chat/view', format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
