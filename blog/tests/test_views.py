from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from blog.models import Post

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testUser')
        Post.objects.create(title='test Post', content='test Post content', author=self.user)

        self.post_create_url = reverse('blog-post_create')
        self.post_update_url = reverse('blog-post_update', args=[Post.objects.get(pk=1).slug])
        self.post_delete_url = reverse('blog-post_delete', args=[Post.objects.get(pk=1).slug])

    def test_post_list_GET(self):
        url = reverse('blog-home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/home.html')

    def test_user_post_list_GET(self):
        url = reverse('blog-user_posts', args=[self.user])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/user_posts.html')

    def test_user_post_list_GET_user_does_not_exist(self):
        """ UserPostListView throws 404 if user with given username does not exist """
        url = reverse('blog-user_posts', args=['testUser0'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_create_POST(self):
        """ PostCreateView creates post for logged in user """
        self.client.force_login(self.user)
        response = self.client.post(self.post_create_url, {'title': 'test Post1', 'content': 'testPost1 content'})
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=2)
        self.assertEqual(post.title, 'test Post1')
        self.assertEqual(post.content, 'testPost1 content')
        self.assertEqual(post.author.id, int(self.client.session['_auth_user_id']))
        self.assertEqual(post.slug, 'test_Post1')
        self.assertRedirects(response, '/post/'+post.slug+'/')

    def test_post_create_POST_no_data(self):
        """ PostCreateView does not create a post if no data is provided """
        self.client.force_login(self.user)
        response = self.client.post(self.post_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')
        posts = Post.objects.all().count()
        self.assertEqual(posts, 1)

    def test_post_create_POST_user_not_logged_in(self):
        """ PostCreateView redirects to login page if user is not logged in """
        response = self.client.post(self.post_create_url, {'title': 'test Post1', 'content': 'testPost1 content'})
        self.assertEqual(response.status_code, 302)
        post = Post.objects.filter(title='test Post1').exists()
        self.assertFalse(post)
        self.assertRedirects(response, '/user/login/?next='+self.post_create_url)

    def test_post_create_POST_already_exists(self):
        """ PostCreateView does not create a new post if given title already exists """
        newUser = User.objects.create(username='newUser')
        self.client.force_login(newUser)
        response = self.client.post(self.post_create_url, {'title': 'test Post', 'content': 'test content'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('blog/post_create.html')
        posts_count = Post.objects.count()
        self.assertEqual(posts_count, 1)
        post = Post.objects.get(pk=1)
        self.assertEqual(post.content, 'test Post content')
        self.assertEqual(post.author, self.user)

    def test_post_detail_GET(self):
        url = reverse('blog-post_detail', args=[Post.objects.get(pk=1).slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')

    def test_post_detail_GET_post_does_not_exist(self):
        """ PostDetailView throws 404 if given post does not exist """
        url = reverse('blog-post_detail', args=['nopost'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_update_POST(self):
        """ PostUpdateView updates post if user is authenticated """
        self.client.force_login(self.user)
        response = self.client.post(self.post_update_url, {'title': 'test Post Updated',
            'content': 'test Post content Updated'})
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=1)
        self.assertEqual(post.title, 'test Post Updated')
        self.assertEqual(post.content, 'test Post content Updated')
        self.assertEqual(post.author.id, int(self.client.session['_auth_user_id']))
        self.assertEqual(post.slug, 'test_Post_Updated')
        self.assertRedirects(response, '/post/'+post.slug+'/')

    def test_post_update_POST_no_data(self):
        """ PostUpdateView does not change post if no update data is provided """
        self.client.force_login(self.user)
        response = self.client.post(self.post_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')
        post = Post.objects.get(pk=1)
        self.assertEqual(post.title, 'test Post')
        self.assertEqual(post.content, 'test Post content')
        self.assertEqual(post.author.id, int(self.client.session['_auth_user_id']))
        self.assertEqual(post.slug, 'test_Post')

    def test_post_update_POST_user_not_logged_in(self):
        """ PostUpdateView redirects to login page if user is not authenticated """
        response = self.client.post(self.post_update_url, {'title': 'test Post Updated'})
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=1)
        self.assertNotEqual(post.title, 'test Post Updated')
        self.assertRedirects(response, '/user/login/?next='+self.post_update_url)

    def test_post_update_POST_user_is_not_author(self):
        """ PostUpdateView throws 403 if logged in user is not an author of post given to update """
        diffUser = User.objects.create(username='diffUser')
        self.client.force_login(diffUser)
        response = self.client.post(self.post_update_url, {'title': 'test Post Update',
            'content': 'test Post content Updated'})
        self.assertEqual(response.status_code, 403)

    def test_post_update_POST_post_does_not_exist(self):
        """ PostUpdateView throws 404 if given post does not exist """
        self.client.force_login(self.user)
        url = reverse('blog-post_update', args=['nopost'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_update_POST_already_exists(self):
        """ PostUpdateView does not update given post if provided title already exists """
        self.client.force_login(self.user)
        Post.objects.create(title='test Post1', content='test Post1 content', author=self.user)
        response = self.client.post(self.post_update_url, {'title': 'test Post1'})
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(pk=1)
        self.assertNotEqual(post.title, 'test Post1')
        self.assertTemplateUsed(response, 'blog/post_form.html')

    def test_post_delete_POST(self):
        self.client.force_login(self.user)
        response = self.client.post(self.post_delete_url)
        self.assertEqual(response.status_code, 302)
        post = Post.objects.filter(pk=1).exists()
        self.assertFalse(post)
        self.assertRedirects(response, '/')

    def test_post_delete_POST_user_not_logged_in(self):
        """ PostDeleteView redirects to login page if no user is logged in """
        response = self.client.post(self.post_delete_url)
        self.assertEqual(response.status_code, 302)
        post = Post.objects.filter(pk=1).exists()
        self.assertTrue(post)
        self.assertRedirects(response, '/user/login/?next='+self.post_delete_url)

    def test_post_delete_POST_user_is_not_author(self):
        """ PostDeleteView throws 403 if logged in user is not an author of post given to delete """
        diffUser = User.objects.create(username='diffUser')
        self.client.force_login(diffUser)
        response = self.client.post(self.post_delete_url)
        self.assertEqual(response.status_code, 403)

    def test_post_delete_POST_post_does_not_exist(self):
        """ PostDeleteView throws 404 if post to delete does not exist """
        self.client.force_login(self.user)
        url = reverse('blog-post_delete', args=['nopost'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_about_GET(self):
        url = reverse('blog-about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/about.html')
