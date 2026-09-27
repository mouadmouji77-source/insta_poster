# posts/urls.py
from django.urls import path
from .views import CreatePostView, ScheduledPostsView

urlpatterns = [
    path('create/', CreatePostView.as_view(), name='create_post'),
    path('scheduled/', ScheduledPostsView.as_view(), name='posteta'),
]
