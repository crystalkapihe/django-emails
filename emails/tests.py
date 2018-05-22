from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client


class EmailsTestCase(TestCase):
    def setUp(self):
        self.credentials = [
            {'username': 'holmes', 'email': 'sherlockholmes@example.com', 'password': 'password1'},
            {'username': 'watson', 'email': 'johnwatson@example.com', 'password': 'password2'},
        ]
        for i in self.credentials:
            User.objects.create_user(**i)

    def test_require_login(self):
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 302)  # redirects
        self.assertEqual('/accounts/login/?next=/', response.url)  # redirects to login

    def test_print_email(self):
        client = Client()
        credentials = self.credentials[0]
        client.login(username=credentials['username'], password=credentials['password'])
        response = client.get('/')
        self.assertTemplateUsed(response, 'home.html')  # uses correct template
        self.assertContains(response, credentials['email'])  # email prints in content

    def test_login_page(self):
        client = Client()
        response = client.get('/login/')
        # contains form fields
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertIs('csrftoken' in client.cookies, True)

    def test_good_login(self):
        credentials = self.credentials[1]
        client = Client()
        client.get('/login/')
        client.post('/login/', {
            'username': credentials['username'],
            'password': credentials['password'],
            'csrfmiddlewaretoken': client.cookies['csrftoken'].value
        })
        # session exists
        self.assertIn('_auth_user_id', client.session)
        # can access home page
        response = client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_bad_password(self):
        credentials = self.credentials[0]
        client = Client()
        client.get('/login/')
        client.post('/login/', {
            'username': credentials['username'],
            'password': 'wrongpassword',
            'csrfmiddlewaretoken': client.cookies['csrftoken'].value
        })
        self.assertNotIn('_auth_user_id', client.session)
        response = client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        client = Client()
        credentials = self.credentials[0]
        client.login(username=credentials['username'], password=credentials['password'])
        # session exists
        self.assertIn('_auth_user_id', client.session)
        client.get('/logout/')
        # session no longer exists
        self.assertNotIn('_auth_user_id', client.session)
