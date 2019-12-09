from django.shortcuts import render

posts = [
    {
        'author': 'user1',
        'title': 'first post',
        'content': 'first post content',
        'date_posted': '11 Dec 2019'
    },
    {
        'author': 'user2',
        'title': 'second post',
        'content': 'second post content',
        'date_posted': '12 Dec 2019'
    }
]

def home(request):
    context = {
        'posts': posts
    }
    return render(request, 'blog/home.html', context)

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
