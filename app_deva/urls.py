from django.urls import path
from .views import protected_view, deva_chat

urlpatterns = [
    path('protected/', protected_view, name='protected_view'),
    path('', deva_chat, name='deva_chat'),
]
