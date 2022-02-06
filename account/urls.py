from django.urls import path
from .views import RegisterPageView, RegisterAPIView, UserInfoAPIView, ProfileAPIView, LoginAPIView

urlpatterns = [
    path("registerPage", RegisterPageView.as_view()),
    path("register", RegisterAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
    path("user/<str:username>", UserInfoAPIView.as_view()),
    path("profile", ProfileAPIView.as_view())
]
