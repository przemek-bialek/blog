from django.urls import path

from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='blog-home'),
    path('<str:username>/', views.UserPostListView.as_view(), name='blog-user_posts'),
    path('post/create/', views.PostCreateView.as_view(), name='blog-post_form'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='blog-post_detail'),
    path('post/<slug:slug>/update/', views.PostUpdateView.as_view(), name='blog-post_update'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='blog-post_delete'),
    path('about/', views.about, name='blog-about'),
]
