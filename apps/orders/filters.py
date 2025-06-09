from django.db.models import F, Func
from django.db.models.expressions import F, Value

from django_filters import rest_framework as filters
from django_filters.rest_framework import OrderingFilter


class NoneIfEmpty(Func):
    function = 'NULLIF'
    arity = 2

    def __init__(self, expression):
        super().__init__(expression, Value(''))


class NullsLastOrderingFilter(OrderingFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        ordering = []
        for param in value:
            if param.startswith('-'):
                field_name = param[1:]
                ordering.append(F(field_name).desc(nulls_last=True))
            else:
                ordering.append(F(param).asc(nulls_last=True))
        return qs.order_by(*ordering)


class OrderFilter(filters.FilterSet):
    course = filters.CharFilter(field_name="course", lookup_expr="iexact")
    course_format = filters.CharFilter(field_name="course_format", lookup_expr="iexact")
    course_type = filters.CharFilter(field_name="course_type", lookup_expr="iexact")
    status = filters.CharFilter(field_name="status", lookup_expr="iexact")
    age = filters.NumberFilter(field_name="age")
    sum = filters.NumberFilter(field_name="sum")
    alreadyPaid = filters.NumberFilter(field_name="alreadyPaid")
    group = filters.NumberFilter(field_name="group", lookup_expr="exact")
    phone = filters.CharFilter(field_name="phone", lookup_expr="icontains")
    created_at = filters.DateTimeFromToRangeFilter(field_name="created_at")
    email = filters.CharFilter(field_name="email", lookup_expr="icontains")
    surname = filters.CharFilter(field_name="surname", lookup_expr="icontains")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    my_orders = filters.BooleanFilter(method="filter_my_orders")
    manager = filters.CharFilter(field_name="manager", method="filter_my_orders")
    order = NullsLastOrderingFilter(
        fields=(
            'id', 'course', 'course_format', 'course_type', 'status',
            'age', 'sum', 'alreadyPaid', 'group', 'phone', 'created_at',
            'email', 'surname', 'name', 'manager',
        )
    )
    ordering_param = "order"

    def filter_my_orders(self, queryset, name, value):
        if value:
            return queryset.filter(manager=self.request.user)
        return queryset

