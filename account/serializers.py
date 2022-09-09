from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.core.cache import cache


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
        fields = ["balance", "avatar_url", "pk", "first_name"]

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

    @staticmethod
    def get_email(obj):
        return obj.email

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


class BlockUserSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, max_length=1000, write_only=True)

    def update(self, instance, validated_data):
        instance.is_active = False
        instance.block_reason = validated_data.get("reason")
        instance.save()
        return instance


class UserInfoSerializer(serializers.ModelSerializer):
    is_current_user = serializers.SerializerMethodField("is_current_session_user")
    is_online = serializers.SerializerMethodField("is_user_online")
    is_current_user_moderator = serializers.SerializerMethodField("is_current_user_staff")

    class Meta:
        model = User
        fields = ("avatar", "description", "is_current_user", "is_online", "first_name", "is_current_user_moderator")

    def is_user_online(self, obj):
        return obj.is_online()

    def is_current_user_staff(self, obj):
        user = self.context.get("request").user
        return user.is_staff

    def is_current_session_user(self, obj):
        """Check if current session user equals input user"""
        current_session_user = self.context.get("request").user
        return obj and current_session_user and current_session_user == obj
        # TODO: test it


class RegisterUserSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255, read_only=True)
    code = serializers.CharField(max_length=50, required=False, write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            tg_id=validated_data.get('tg_id')
        )
        user.save()
        token = Token.objects.create(user=user)

        return {
            "token": token.key
        }

    def validate(self, data):
        code = data.get('code')
        if not code:
            raise serializers.ValidationError({'code': 'Код не указан!'})
        tg_id = cache.get(f'register_code_{code}')

        if not tg_id:
            raise serializers.ValidationError({'code': 'Код неверный'})

        cache.delete(f'register_code_{code}')
        return {
            "tg_id": tg_id
        }


class LoginSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50, write_only=True, required=False)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        code = data.get('code')
        if not code:
            raise serializers.ValidationError({'code': 'Код не указан!'})

        tg_id = cache.get(f'login_code_{code}')
        if not tg_id:
            raise serializers.ValidationError({'code': 'Код неверный'})

        cache.delete(f'login_tg_{tg_id}')
        cache.delete(f'login_code_{code}')
        user = User.objects.get(tg_id=tg_id)
        if not user.is_active:
            raise serializers.ValidationError(
                {'code': 'Пользователь был заблокирован по причине: ' + user.block_reason}
            )
        token, _ = Token.objects.get_or_create(user=user)

        return {
            'token': token
        }
