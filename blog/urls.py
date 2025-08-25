

# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # The home page for the blog posts list
    path('', views.PostListView.as_view(), name='post-list'),  # <-- Ensure this line is present
    
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<slug:slug>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add-comment'),
]