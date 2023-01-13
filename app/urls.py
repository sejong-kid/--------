from django.urls import path, include
from . import views
urlpatterns = [
    # path('upload/', views.upload),
    path('', views.index),
    path('page2/', views.page2),
    # path('read/', views.read),
    # path('home/', views.home),
    # path('search/', views.search),
    # path('article/', views.article),
]
