from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from rest_framework import serializers

from apps.users.models import ProfileModel

UserModel = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = ProfileModel
        fields = ('id', 'first_name', 'last_name', 'age', 'avatar')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    total_orders = serializers.IntegerField(read_only=True)
    orders_new = serializers.IntegerField(read_only=True)
    orders_in_work = serializers.IntegerField(read_only=True)
    orders_agree = serializers.IntegerField(read_only=True)
    orders_disagree = serializers.IntegerField(read_only=True)
    orders_dubbing = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserModel
        fields = (
            'id', 'username', 'email', 'password', 'is_manager', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'created_at',
            'updated_at', 'profile', 'total_orders', 'orders_new', 'orders_in_work', 'orders_agree',
            'orders_disagree', 'orders_dubbing',
        )
        read_only_fields = ('id', 'is_active', 'is_manager', 'is_staff', 'is_superuser', 'last_login', 'created_at', 'updated_at')
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    @atomic
    def create(self, validated_data: dict):
        profile = validated_data.pop('profile')
        user = UserModel.objects.create_user(**validated_data)
        ProfileModel.objects.create(**profile, user=user)
        return user
