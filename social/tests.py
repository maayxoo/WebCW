from django.test import TestCase
from django.contrib import auth

from social.models import User

TEST_USERNAME = 'test'
TEST_PASSWORD = 'test123'

class SignuUpTest(TestCase):

    def setUp(self):
        test = User.objects.create(username=TEST_USERNAME)
        test.set_password(TEST_PASSWORD)
        test.save()

    def test_test_password_set(self):
        user = auth.authenticate(username=TEST_USERNAME, password=TEST_PASSWORD)
        self.assertIsNotNone(user)