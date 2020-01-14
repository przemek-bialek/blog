from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from PIL import Image

import tempfile
import shutil
import os

from user.models import Profile

class TestViews(TestCase):
    def _create_img_file(self, color='white', size=(200, 200)):
        file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img = Image.new('RGB', size, color)
        img.save(file, 'JPEG')
        return SimpleUploadedFile('test.jpg', open(file.name, 'rb').read(), content_type='image/jpg')


    @classmethod
    def setUpClass(self):
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)
        img = Image.new('RGB', (200, 200), 'black')
        img.save(settings.MEDIA_ROOT+'/default.jpg', 'JPEG')

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(settings.MEDIA_ROOT)


    def setUp(self):
        self.testUser = User.objects.create(username='testUser', email='testUser@email.com', password='somepassword')

        self.register_url = reverse('user-register')
        self.profile_url = reverse('user-profile')

    def tearDown(self):
        #os.remove(settings.MEDIA_ROOT+'/test.jpg')
        pass


    def test_register_POST(self):
        response = self.client.post(self.register_url, {'username': 'newUser', 'email': 'newUser@email.com',
            'password1': 'somepassword', 'password2': 'somepassword'})
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(pk=2)
        self.assertEqual(user.username, 'newUser')
        self.assertEqual(user.email, 'newUser@email.com')
        self.assertTrue(user.check_password('somepassword'))
        self.assertEqual(user.profile.img.url, '/media/default.jpg')
        self.assertRedirects(response, '/user/login/')

    def test_register_POST_no_data(self):
        """ register view does not create user if no data is provided """
        response = self.client.post(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')
        user = User.objects.filter(pk=2).exists()
        self.assertFalse(user)

    def test_register_POST_username_exists(self):
        """ register view does not create user if provided username already exists """
        response = self.client.post(self.register_url, {'username': 'testUser', 'email': 'someemail@email.com',
            'password1': 'somepassword2', 'password2': 'somepassword2'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')
        users_count = User.objects.count()
        self.assertEqual(users_count, 1)
        user = User.objects.get(pk=1)
        self.assertEqual(user.email, 'testUser@email.com')
        self.assertEqual(user.password, 'somepassword')

    #TO DO:
    def test_register_POST_email_exists(self):
        """ register does not create new user if provided email is already in use """
        response = self.client.post(self.register_url, {'username': 'newUser', 'email': 'testUser@email.com',
            'password1': 'somepassword2', 'password2': 'somepassword2'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')
        users_count = User.objets.count()
        self.assertEqual(users_count, 1)
        user = User.objects.get(pk=1)
        self.assertEqual(user.username, 'testUser')
        self.assertEqual(user.password, 'somepassword')

    def test_register_GET(self):
        response = self.client.get(self.register_url, {'username': 'newUser', 'email': 'newUser@email.com',
            'password1': 'somepassword2', 'password2': 'somepassword2'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')
        users_count = User.objects.count()
        self.assertEqual(users_count, 1)

    def test_profile_POST(self):
        self.client.force_login(self.testUser)
        pic = self._create_img_file()
        response = self.client.post(self.profile_url, {'img': pic, 'username': 'newname',
            'email': 'newname@email.com'})
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(pk=1)
        self.assertEqual(user.username, 'newname')
        self.assertEqual(user.email, 'newname@email.com')
        self.assertEqual(user.password, 'somepassword')
        self.assertEqual(user.profile.img, 'profile_pics/test.jpg')
        self.assertRedirects(response, '/user/profile/')

    def test_profile_POST_no_data(self):
        """ profile view does not change logged in user's profile if no data is provided """
        self.client.force_login(self.testUser)
        response = self.client.post(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')
        user = User.objects.get(pk=1)
        self.assertEqual(user.username, 'testUser')
        self.assertEqual(user.email, 'testUser@email.com')
        self.assertEqual(user.password, 'somepassword')
        self.assertEqual(user.profile.img, 'default.jpg')

    def test_profile_POST_user_not_logged_in(self):
        """ profile view redirects to login page if no user is logged in """
        response = self.client.post(self.profile_url, {'username': 'newUser'})
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(pk=1)
        self.assertNotEqual(user.username, 'newUser')
        self.assertRedirects(response, '/user/login/?next='+self.profile_url)

    def test_profile_POST_username_exists(self):
        """ profile view does not change user's profile if provided username is already in use """
        User.objects.create(username='newUser')
        self.client.force_login(self.testUser)
        response = self.client.post(self.profile_url, {'username': 'newUser'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')
        user = User.objects.get(pk=1)
        self.assertNotEqual(user.username, 'newUser')

    #TO DO:
    def test_profile_POST_email_in_use(self):
        """ profile view does not change user's email if provided email is already used """
        User.objects.create(username='newUser', email='newUser@email.com')
        self.client.force_login(self.testUser)
        response = self.client.post(self.profile_url, {'username': 'somename', 'email': 'newUser@email.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')
        user = User.objects.get(pk=1)
        self.assertNotEqual(user.email, 'newUser@email.com')

    def test_profile_GET(self):
        pic = self._create_img_file()
        self.client.force_login(self.testUser)
        response = self.client.get(self.profile_url, {'img': pic, 'username': 'newName', 'email': 'newmail@email.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')
        user = User.objects.get(pk=1)
        self.assertNotEqual(user.username, 'newName')
        self.assertNotEqual(user.email, 'newmail@email.com')
        self.assertNotEqual(user.profile.img, 'profile_pics/test.jpg')
