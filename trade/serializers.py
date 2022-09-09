from rest_framework import serializers

from .models import *


class GoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodCategory
        exclude = ['parent', ]


class GoodSerializer(serializers.ModelSerializer):

    def validate(self, data):
        data = super().validate(data)
        if data.get('type') == Good.TYPE_GOOD and 'condition' not in data:
            raise serializers.ValidationError("Состояние предмета (от 1 до 5) является обязательным для товара")
        return data

    class Meta:
        model = Good
        fields = '__all__'
        extra_kwargs = {
            'state': {'read_only': True},
            'user': {'read_only': True},
        }


