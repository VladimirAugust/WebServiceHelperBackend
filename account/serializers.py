from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.core.cache import cache
from django.conf import settings
from .services.registration import generate_confirm_code, send_confirm_code
from telebot.apihelper import ApiTelegramException


User = get_user_model()


class UserChangeAvatarSerializer(serializers.Serializer):
    avatar = serializers.ImageField(required=True)

    def update(self, instance, validated_data):
        instance.avatar = validated_data["avatar"]
        instance.save()
        return instance


class UserPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, max_length=64)
    new_password = serializers.CharField(required=True, max_length=64)

    def validate(self, data):
        """add here additional check for password strength if needed"""
        if not self.context.get('request').user.check_password(data.get("old_password")):
            raise serializers.ValidationError({'old_password': 'Wrong password.'})
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

    def create(self, validated_data):
        pass

    @property
    def data(self):
        """just return success dictionary. you can change this to your need, but i dont think output should be user
        data after password change """
        return {'Success': True}


class ProfileSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField("get_balance")
    avatar_url = serializers.SerializerMethodField("get_avatar_url")

    class Meta:
        model = User
        fields = ["balance", "avatar_url", "username"]

    @staticmethod
    def get_balance(obj):
        return obj.gifts

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.avatar.url)


class UserSettingsSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=True)
    district = serializers.CharField(max_length=100, required=True)
    phone_number = serializers.CharField(required=True)

    email = serializers.SerializerMethodField("get_email")
    avatar = serializers.SerializerMethodField("get_avatar")
    username = serializers.SerializerMethodField("get_username")

    @staticmethod
    def get_email(obj):
        return obj.email

    @staticmethod
    def get_username(obj: User):
        return obj.username

    def get_avatar(self, obj: User):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.avatar.url)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.city = validated_data.get('city', instance.city)
        instance.district = validated_data.get('district', instance.district)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()
        return instance


class UserInfoSerializer(serializers.ModelSerializer):
    is_current_user = serializers.SerializerMethodField("is_current_session_user")
    is_online = serializers.SerializerMethodField("is_user_online")

    class Meta:
        model = User
        fields = ("username", "avatar", "description", "is_current_user", "is_online")

    def is_user_online(self, obj):
        return obj.is_online()

    def is_current_session_user(self, obj):
        """Check if current session user equals input user"""
        current_session_user = self.context.get("request").user
        if obj and current_session_user:
            if current_session_user == obj:
                return True
        return False


class RegisterUserSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=20)
    code = serializers.CharField(max_length=50, required=False)
    step = serializers.IntegerField(required=True, write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            phone_number=validated_data.get('phone_number')
        )
        return user

    def validate(self, data):
        step = data.get('step')
        phone_number = data.get('phone_number')
        try:
            User.objects.get(phone_number=phone_number)
            raise serializers.ValidationError({"phone_number": "Пользователь с таким номером телефона уже существует"})
        except User.DoesNotExist:
            pass

        if step == 1:   # set phone number
            code = generate_confirm_code()
            cache.set(f'register_{phone_number}', code, settings.USER_CONFIRM_PHONE_NUMBER_TIMEOUT)
            try:
                send_confirm_code(phone_number, code, settings.CONFIRM_REGISTER_MESSAGE)
            except ApiTelegramException:
                raise serializers.ValidationError({"phone_number": "Такого номера не существует"})
            return data
        else:
            code = data.get('code')
            if not code:
                raise serializers.ValidationError('Код не указан!')
            confirm_code = cache.get(f'register_{phone_number}')
            if code == confirm_code:
                return data
            else:
                raise serializers.ValidationError('Код неверный')


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=True)
    code = serializers.CharField(max_length=50, write_only=True, required=False)
    step = serializers.IntegerField(required=True, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        step = data.get('step')

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким номером телефона не найден!")

        if not user.is_active:
            raise serializers.ValidationError(
                'Пользователь был деактивирован'
            )

        if step == 1:
            code = generate_confirm_code()
            cache.set(f'login_{phone_number}', code, settings.USER_CONFIRM_PHONE_NUMBER_TIMEOUT)
            try:
                send_confirm_code(phone_number, code, settings.CONFIRM_LOGIN_MESSAGE)
            except ApiTelegramException:
                raise serializers.ValidationError({"phone_number": "Такого номера не существует"})
            return data
        else:
            code = data.get('code')
            if not code:
                raise serializers.ValidationError('Код не указан!')
            confirm_code = cache.get(f'login_{phone_number}')
            if code == confirm_code:
                token, _ = Token.objects.get_or_create(user=user)

                return {
                    'phone_number': user.phone_number,
                    'token': token
                }
            else:
                raise serializers.ValidationError('Код неверный')
