import math

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PagePagination(PageNumberPagination):
    page_size = 25
    max_page_size = 25
    page_size_query_param = 'size'

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('all') == 'true':
            return None
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        count = self.page.paginator.count
        total_pages = math.ceil(count / self.get_page_size(self.request))
        return Response({
            'total_items': count,
            'total_pages': total_pages,
            'prev': bool(self.get_previous_link()),
            'next': bool(self.get_next_link()),
            'data': data,
        }, status.HTTP_200_OK)

