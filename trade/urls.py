from django.template.defaulttags import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

api_router = DefaultRouter()
api_router.register(r'good', GoodsViewSet, 'good')

urlpatterns = [
    path("categories", CategoriesAPIView.as_view()),
]

urlpatterns += api_router.urls
