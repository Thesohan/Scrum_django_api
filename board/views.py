from django.contrib.auth import get_user_model
from rest_framework import authentication, permissions, viewsets, filters
from .models import Sprint, Task
from .serializers import SprintSerializer, TaskSerializer ,UserSerializer
from .forms import TaskFilter, SprintFilter
# Create your views here.

User = get_user_model()

class DefaultsMixin(object):
    """
    Default settings for view authentication, permissions, filtering and paginatioin.
    """

    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication
    )

    permission_classes= (
        permissions.IsAuthenticated,
    )
    paginated_by = 25
    paginated_by_param = 'page_size'
    max_paginate_bu = 100
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )



class SprintViewSet(DefaultsMixin,viewsets.ModelViewSet):
    """
    API endpoint for listing and creating sprints.
    """

    queryset = Sprint.objects.order_by('end')   
    serializer_class = SprintSerializer
    filter_class = SprintFilter
    search_fields =['name','end']
    ordering_fields = ['end','name',]

class TaskViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """
    API endpoint for listing and creating tasks.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_class = TaskFilter
    search_fields = ['name','description']
    ordering_fields = ('order','name','started','due','completed')

class UserViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for listing users.
    This does not expose the actions to create new users or to edit existing ones through
    the API.
    """

    lookup_field = User.USERNAME_FIELD
    lookup_url_kwarg = User.USERNAME_FIELD
    queryset = User.objects.order_by(User.USERNAME_FIELD)
    serializer_class = UserSerializer
    search_fields = [User.USERNAME_FIELD]



    