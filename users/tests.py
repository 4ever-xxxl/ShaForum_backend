from django.test import TestCase

# Create your tests here.

class UserRegisterTests(TestCase):
    def test_register_status_code(self):
        response = self.client.get('/api/register/')
        self.assertEqual(response.status_code, 200)