from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Sprint, Task
from rest_framework.reverse import reverse

User = get_user_model()

class SprintSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField('get_links')
    class Meta:
        model = Sprint
        fields = ('id','name','description','end','links',)

    def get_links(self,obj):
        request = self.context['request']
        return {
            'self':reverse(
                'sprint-detail',
                kwargs={
                    'pk':obj.pk
                    },
                request=request
                )
            }

class TaskSerializer(serializers.ModelSerializer):

    """
    Serializes Task object
    """
    # Status_display is a read-only field to be serialized that returns the value of the
    # Get_status_display method on the serializer.
    status_display = serializers.SerializerMethodField('get_status_display')
    assigned = serializers.SlugRelatedField(
        slug_field=User.USERNAME_FIELD,required= False,read_only=True
    )
    links = serializers.SerializerMethodField('get_links')
    class Meta:
        model = Task
        fields = ('id','name','description','sprint','status','status_display','order','assigned','started','due','completed','links')

    def get_links(self,obj):
        request = self.context['request']
        links = {
            'self':reverse('task-detail',
            kwargs={
                'pk':obj.pk
            },
            request=request,
            ),
            'sprint':None,
            'assigned':None
        }
        if obj.sprint_id:
            links['sprint']=reverse('sprint-detail',
            kwargs={'pk':obj.sprint_id},
            request=request
            )
        if obj.assigned:
            links['assigned']=reverse('user-detail',
            kwargs={User.USERNAME_FIELD:obj.assigned},
            request=request
            )

        return links

    def get_status_display(self,obj):
        return obj.get_status_display()    

    
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name',read_only = True)
    links = serializers.SerializerMethodField('get_links')

    class Meta:
        model = User
        fields = ('id',User.USERNAME_FIELD,'full_name','is_active','links')

    def get_links(self,obj):
        return {
            'self':reverse('user-detail',
            kwargs={
                User.USERNAME_FIELD:obj.get_username()
            },
            request=self.context['request']
            )
        }

