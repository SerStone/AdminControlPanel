from rest_framework import serializers

from core.enums import CourseEnum, CourseFormatEnum, CourseTypeEnum, StatusEnum

from apps.orders.fields import EnumChoiceField
from apps.orders.models import CommentModel, GroupModel, OrderModel
from apps.users.serializers import UserSerializer


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupModel
        fields = ["id", "group_name"]

    def validate_group_name(self, value):
        if GroupModel.objects.filter(group_name=value).exists():
            raise serializers.ValidationError("Group with this name already exists.")
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = CommentModel
        fields = ('id', 'text', 'author', 'created_at')


class OrderSerializer(serializers.ModelSerializer):
    manager = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    group = GroupSerializer(read_only=True)
    group_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    age = serializers.IntegerField(allow_null=True, required=False)
    sum = serializers.IntegerField(allow_null=True)
    alreadyPaid = serializers.IntegerField(allow_null=True)

    course = EnumChoiceField(enum_class=CourseEnum, allow_null=True)
    course_format = EnumChoiceField(enum_class=CourseFormatEnum, allow_null=True)
    course_type = EnumChoiceField(enum_class=CourseTypeEnum, allow_null=True)
    status = EnumChoiceField(enum_class=StatusEnum, allow_null=True)

    def check_and_update_dubbing_status(self, email):
        if email:
            duplicate_orders = OrderModel.objects.filter(email=email).exclude(status="Dubbing")
            if duplicate_orders.count() > 1:
                duplicate_orders.update(status="Dubbing")

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['manager'] = user
        validated_data['status'] = "New"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        group_id = validated_data.pop('group_id', None)
        email = validated_data.get('email', instance.email)
        user = self.context['request'].user

        if instance.manager is None:
            validated_data['manager'] = user

            if 'status' not in validated_data or validated_data['status'] is None:
                validated_data['status'] = "In work"

        if group_id is not None:
            try:
                instance.group = GroupModel.objects.get(id=group_id)
            except GroupModel.DoesNotExist:
                raise serializers.ValidationError({"group_id": "Group not found"})

        instance = super().update(instance, validated_data)

        self.check_and_update_dubbing_status(email)

        return instance

    class Meta:
        model = OrderModel
        fields = ('id', 'name', 'surname', 'email', 'phone', 'age', 'course', 'course_format',
                  'course_type', 'sum','group_id', 'alreadyPaid', 'utm', 'msg', 'status', 'created_at', "group", "manager",
                  'comments')
