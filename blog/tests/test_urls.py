from django.test import SimpleTestCase
from django.urls import reverse, resolve

from blog.views import (PostListView, UserPostListView, PostCreateView, PostDetailView, PostUpdateView, PostDeleteView,
                        about)

class TestUrls(SimpleTestCase):
    def test_home_url_resolves(self):
        url = reverse('blog-home')
        self.assertEqual(resolve(url).func.view_class, PostListView)

    def test_user_posts_url_resolves(self):
        url = reverse('blog-user_posts', args=['test-username'])
        self.assertEqual(resolve(url).func.view_class, UserPostListView)

    def test_post_create_url_resolves(self):
        url = reverse('blog-post_create')
        self.assertEqual(resolve(url).func.view_class, PostCreateView)

    def test_post_detail_url_resolves(self):
        url = reverse('blog-post_detail', args=['test-slug'])
        self.assertEqual(resolve(url).func.view_class, PostDetailView)

    def test_post_update_url_resolves(self):
        url = reverse('blog-post_update', args=['test-slug'])
        self.assertEqual(resolve(url).func.view_class, PostUpdateView)

    def test_post_delete_url_resolves(self):
        url = reverse('blog-post_delete', args=['test-slug'])
        self.assertEqual(resolve(url).func.view_class, PostDeleteView)

    def test_about_url_resolves(self):
        url = reverse('blog-about')
        self.assertEqual(resolve(url).func, about)
