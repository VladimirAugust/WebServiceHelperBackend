from rest_framework import serializers

from .models import *


class GoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodCategory
        exclude = ['parent', ]


class GoodSerializer(serializers.ModelSerializer):
    images = serializers.JSONField(write_only=True, required=False)
    images_for_read = serializers.SerializerMethodField('get_images')
    is_author = serializers.SerializerMethodField('get_is_author')

    def validate(self, data):
        data = super().validate(data)

        is_good = False
        if is_good and 'condition' not in data:
            raise serializers.ValidationError("Состояние предмета (от 1 до 5) является обязательным для товара")
        return data

    class Meta:
        model = Good
        fields = '__all__'
        extra_kwargs = {
            'state': {'read_only': True},
            'user': {'read_only': True},
            'moderation_disallow_reason': {'read_only': True},
        }

    @staticmethod
    def get_images(obj):
        return map(lambda x: x.image.name, obj.images.all())



    def get_is_author(self, obj):
        request = self.context.get("request")
        return request and hasattr(request, "user") and obj.user == request.user

class UploadedImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_name')
    name = serializers.SerializerMethodField('get_id')
    class Meta:
        model = UploadedImage
        fields = ('name', 'url')

    def get_name(self, obj):
        return obj.image.name

    def get_id(self, obj):
        return obj.id

