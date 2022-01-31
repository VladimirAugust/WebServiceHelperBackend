from django.urls import path
from .views import RegisterPageView, RegisterAPIView, UserInfoAPIView

urlpatterns = [
    path("registerPage", RegisterPageView.as_view()),
    path("register", RegisterAPIView.as_view()),
    path("user/<str:username>", UserInfoAPIView.as_view())
]
