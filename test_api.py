import unittest
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key-32-bytes-minimum-length-for-hmac!'
    JWT_SECRET_KEY = 'test-jwt-secret-key-32-bytes-minimum-length!'

class ContactsAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

        # Register and login test user
        reg_resp = self.client.post('/api/auth/register', json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secretpassword"
        })
        self.token = reg_resp.get_json()['access_token']
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_01_user_register_and_login(self):
        """Test User Registration and Login with Bcrypt password verification."""
        login_resp = self.client.post('/api/auth/login', json={
            "email": "john@example.com",
            "password": "secretpassword"
        })
        self.assertEqual(login_resp.status_code, 200)
        data = login_resp.get_json()
        self.assertIn('access_token', data)
        self.assertEqual(data['user']['email'], 'john@example.com')

    def test_02_create_contacts(self):
        """Test Creating normal and hidden contacts."""
        # Create normal contact
        c1 = self.client.post('/create', headers=self.headers, json={
            "name": "Alice Smith",
            "ph_no": "1234567890",
            "email": "alice@example.com",
            "company_name": "Acme Corp"
        })
        self.assertEqual(c1.status_code, 201)

        # Create hidden contact with hide_code
        c2 = self.client.post('/create', headers=self.headers, json={
            "name": "Secret Agent",
            "ph_no": "9998887776",
            "email": "agent@topsecret.com",
            "company_name": "MI6",
            "hide_code": "SECRET007"
        })
        self.assertEqual(c2.status_code, 201)

    def test_03_get_contacts_hidden_logic(self):
        """Test fetching contacts list hides hidden contacts by default."""
        # Add normal and hidden contact
        self.client.post('/create', headers=self.headers, json={
            "name": "Normal Contact", "ph_no": "111"
        })
        self.client.post('/create', headers=self.headers, json={
            "name": "Hidden Contact", "ph_no": "222", "hide_code": "VAULT123"
        })

        # General GET /get (No code passed)
        res = self.client.get('/get', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        contacts = res.get_json()['contacts']
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]['name'], "Normal Contact")

        # GET /get with code=VAULT123
        res_hidden = self.client.get('/get?code=VAULT123', headers=self.headers)
        self.assertEqual(res_hidden.status_code, 200)
        hidden_contacts = res_hidden.get_json()['contacts']
        self.assertEqual(len(hidden_contacts), 1)
        self.assertEqual(hidden_contacts[0]['name'], "Hidden Contact")

    def test_04_search_contacts_hidden_logic(self):
        """Test searching contacts hides hidden contacts unless code is provided."""
        self.client.post('/create', headers=self.headers, json={
            "name": "Bruce Wayne", "ph_no": "100", "company_name": "Wayne Enterprises"
        })
        self.client.post('/create', headers=self.headers, json={
            "name": "Batman", "ph_no": "911", "company_name": "Justice League", "hide_code": "BATCAVE"
        })

        # General search for "Wayne"
        res1 = self.client.get('/search?q=Wayne', headers=self.headers)
        self.assertEqual(len(res1.get_json()['contacts']), 1)
        self.assertEqual(res1.get_json()['contacts'][0]['name'], "Bruce Wayne")

        # General search for "Batman" (without code) -> should return 0 results
        res2 = self.client.get('/search?q=Batman', headers=self.headers)
        self.assertEqual(len(res2.get_json()['contacts']), 0)

        # Search for "Batman" with hide code "BATCAVE" -> should reveal Batman!
        res3 = self.client.get('/search?q=Batman&code=BATCAVE', headers=self.headers)
        self.assertEqual(len(res3.get_json()['contacts']), 1)
        self.assertEqual(res3.get_json()['contacts'][0]['name'], "Batman")

    def test_05_update_and_delete(self):
        """Test updating and deleting contacts."""
        c = self.client.post('/create', headers=self.headers, json={
            "name": "Charlie", "ph_no": "555"
        }).get_json()['contact']

        c_id = c['c_id']

        # Update
        up_res = self.client.put(f'/update/{c_id}', headers=self.headers, json={
            "company_name": "New Tech Inc",
            "ph_no": "777"
        })
        self.assertEqual(up_res.status_code, 200)
        self.assertEqual(up_res.get_json()['contact']['company_name'], "New Tech Inc")

        # Delete
        del_res = self.client.delete(f'/delete/{c_id}', headers=self.headers)
        self.assertEqual(del_res.status_code, 200)

        # Verify deleted
        get_res = self.client.get(f'/get/{c_id}', headers=self.headers)
        self.assertEqual(get_res.status_code, 404)

    def test_06_custom_error_handlers(self):
        """Test 404 and 500 error responses in JSON format."""
        # 404 test
        res_404 = self.client.get('/non-existent-endpoint')
        self.assertEqual(res_404.status_code, 404)
        self.assertEqual(res_404.get_json()['error'], "Not Found")

        # 500 test
        res_500 = self.client.get('/test-500')
        self.assertEqual(res_500.status_code, 500)
        self.assertEqual(res_500.get_json()['error'], "Internal Server Error")

    def test_07_secure_photo_uploads(self):
        """Test secure photo serving endpoints (JWT Auth & Ownership verification)."""
        # Create a contact with a photo_file name
        self.client.post('/create', headers=self.headers, json={
            "name": "Photo Test", "ph_no": "111", "photo_file": "user_photo.jpg"
        })

        # 1. Unauthenticated request -> 401 Unauthorized
        res_unauth = self.client.get('/uploads/user_photo.jpg')
        self.assertEqual(res_unauth.status_code, 401)

        # 2. Request for non-existent / unowned photo -> 403 Forbidden
        res_unowned = self.client.get('/uploads/other_user_photo.jpg', headers=self.headers)
        self.assertEqual(res_unowned.status_code, 403)


if __name__ == '__main__':
    unittest.main()

