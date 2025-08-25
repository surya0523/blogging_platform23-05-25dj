# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Add your user-related URL patterns here
    path('signup/', views.signup, name='signup'),
    
    
    # You can also add more URLs for user profiles, etc.
]