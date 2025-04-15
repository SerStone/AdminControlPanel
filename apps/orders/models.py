from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.enums import CourseEnum, CourseTypeEnum, StatusEnum
from core.models import BaseModel

UserModel = get_user_model()


class GroupModel(models.Model):
    class Meta:
        db_table = 'groups'
        ordering = ['-id']

    group_name = models.CharField(max_length=25, unique=True, blank=True, null=True)

    def __str__(self):
        return self.group_name


class OrderModel(models.Model):
    class Meta:
        db_table = 'orders'
        ordering = ['-id']

    name = models.CharField(max_length=25, blank=True, null=True)
    surname = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], blank=True, null=True)
    course = models.CharField(max_length=10, choices=CourseEnum.choices, blank=True, null=True)
    course_format = models.CharField(max_length=15, blank=True, null=True)
    course_type = models.CharField(max_length=100, choices=CourseTypeEnum.choices, blank=True, null=True)
    sum = models.IntegerField(blank=True, null=True)
    alreadyPaid = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    utm = models.CharField(max_length=100, blank=True, null=True)
    msg = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=15, choices=StatusEnum.choices, blank=True, null=True)
    manager = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_orders'
    )
    group = models.ForeignKey(
        GroupModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='groups_orders'
    )


class CommentModel(models.Model):
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']