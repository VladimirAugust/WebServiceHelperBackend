from django.urls import path
from .views import RegisterAPIView, UserInfoAPIView, ProfileAPIView, LoginAPIView, SettingsAPIView, \
    APIChangePasswordView, UploadAvatarAPIView


urlpatterns = [
    path("register", RegisterAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
    path("profile", ProfileAPIView.as_view()),
    path("password/change", APIChangePasswordView.as_view()),
    path("settings", SettingsAPIView.as_view()),
    path("user/<str:username>", UserInfoAPIView.as_view()),
    path("image/upload", UploadAvatarAPIView.as_view())
]
