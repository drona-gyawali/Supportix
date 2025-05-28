import shutil
import tempfile
from io import BytesIO

from chat.models import ChatGroup, GroupMessage
from core.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase


def generate_test_image():
    img_io = BytesIO()
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))
    image.save(img_io, format="PNG")
    img_io.seek(0)
    return SimpleUploadedFile("test.png", img_io.read(), content_type="image/png")


TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ChatAPITest(APITestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT)

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass"
        )

        self.client.login(username="testuser", password="testpass")

        self.group = ChatGroup.objects.create(group_name="Test Group")
        self.group_name = self.group.group_name

        self.message = GroupMessage.objects.create(
            group=self.group, author=self.user, body="Hello World"
        )

        self.file_url = reverse("upload-file")
        self.image_url = reverse("upload-image")

    def test_create_message(self):
        url = reverse("chat-message-create")
        data = {"group": self.group.id, "author": self.user.id, "body": "Test message"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GroupMessage.objects.count(), 2)

    def test_update_group(self):
        url = reverse("chat-group-update", kwargs={"group_name": self.group_name})
        response = self.client.put(url, {"group_name": "Updated Group"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.group.refresh_from_db()
        self.assertEqual(self.group.group_name, "Updated Group")

    def test_delete_message_by_non_owner(self):
        url = reverse("chat-message-delete", kwargs={"id": self.message.id})
        self.client.logout()
        self.client.login(username="otheruser", password="testpass")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_valid_pdf_upload(self):
        file = SimpleUploadedFile(
            "document.pdf", b"file_content", content_type="application/pdf"
        )
        response = self.client.post(
            self.file_url,
            {
                "file": file,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_extension_file_upload(self):
        file = SimpleUploadedFile(
            "document.txt", b"file_content", content_type="text/plain"
        )
        response = self.client.post(
            self.file_url,
            {
                "file": file,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail_error", response.data)

    def test_large_file_upload(self):
        big_file = SimpleUploadedFile(
            "large.pdf", b"x" * (20 * 1024 * 1024 + 1), content_type="application/pdf"
        )
        response = self.client.post(
            self.file_url,
            {
                "file": big_file,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_image_upload(self):
        img = generate_test_image()
        response = self.client.post(
            self.image_url,
            {
                "image": img,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_image_extension(self):
        img = SimpleUploadedFile("image.txt", b"img_content", content_type="text/plain")
        response = self.client.post(
            self.image_url,
            {
                "image": img,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_large_image_upload(self):
        big_img = SimpleUploadedFile(
            "image.png", b"x" * (5 * 1024 * 1024 + 1), content_type="image/png"
        )
        response = self.client.post(
            self.image_url,
            {
                "image": big_img,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
