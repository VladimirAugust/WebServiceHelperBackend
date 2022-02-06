from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .services.user_services import get_user_by_name, get_user_by_request
from .services.registration import is_link_valid, create_user
from .serializers import RegisterUserSerializer, RegisterPageSerializer, UserInfoSerializer, LoginSerializer
from .exceptions import UserAlreadyExist, URLHashDoesNotExist
from django.contrib.auth import get_user_model


User = get_user_model()


class RegisterPageView(APIView):
    """
    Проверяет валидная ли ссылка для регистрации
    """
    permission_classes = (AllowAny,)
    serializer_class = RegisterPageSerializer

    def post(self, request) -> Response:
        serializer = RegisterPageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validate(request.data)
            if is_link_valid(data["url_hash"]):
                return Response({}, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_404_NOT_FOUND)


class LoginAPIView(APIView):
    """This view authenticate user. It returns token"""
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileAPIView(APIView):
    """
    This view returns current user info:
    balance, avatar url, username, etc
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = get_user_by_request(request)
        except Token.DoesNotExist:
            return Response({"error": "Token does not exist"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            "balance": user.gifts,
            "avatar_url": request.build_absolute_uri(user.avatar.url),
            "username": user.username,
        }, status=status.HTTP_200_OK)


class UserInfoAPIView(APIView):
    """Возращает информацию о юзере."""
    permission_classes = (AllowAny,)
    serializer_class = UserInfoSerializer

    def get(self, request, username):
        try:
            user = get_user_by_name(username)
        except User.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserInfoSerializer(user, context={
            "request": request
        })
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer

    def post(self, request) -> Response:
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validate(request.data)
            try:
                token = create_user(data["username"], data["email"], data["password"], data["url_hash"])
                return Response({"token": token}, status=status.HTTP_200_OK)
            except UserAlreadyExist:
                return Response({"error_message": "Username or email is already exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            except URLHashDoesNotExist:
                pass

        return Response({}, status=status.HTTP_404_NOT_FOUND)
