from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Sprint, Task
from rest_framework.reverse import reverse
from datetime import date
from django.utils.translation import ugettext_lazy as _
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
                ),
                'tasks':reverse('task-list',
                request=request)+'?sprint={}'.format(obj.pk),
            }

    # Each serializer field has a validate_<field>(field value)
    # hook that is called to perform additional validations on the field
    def validate_end(self,value):
        new = self.instance is None
        changed = self.instance and self.ins.end != value

        if (new or changed) and (value < date.today()):
            msg = _('End date connot be in the past.')
            raise serializers.ValidationError(msg)
        return value 

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

    def validate_sprint(self,value):
        
        if self.initial_data and self.initial_data.get('sprint'):
            if value != self.initial_data.get('sprint'):
                if self.initial_data.get('status') == Task.STATUS_DONE:
                   msg = _('Cannot change the sprint of a completed task.')
                   raise serializers.ValidationError(msg)

                if value and value.end < date.today():
                    msg = _('Cannot assign tasks to past sprints.')
                    raise serializers.ValidationError(msg)
        else:
            if value and value.end < date.today():
                msg = _('Cannot add tasks to past sprints.')
                raise serializers.ValidationError(msg)
        return value

    # def validate(self, attrs):
    #     sprint = attrs.get('sprint')
    #     status = attrs.get('status', Task.STATUS_TODO)
    #     started = attrs.get('started')
    #     completed = attrs.get('completed')
    #     print(sprint,started,status,completed)
    #     if not sprint and status != Task.STATUS_TODO:
    #         msg = _('Backlog tasks must have "Not Started" status.')
    #         raise serializers.ValidationError(msg)
    #     if started and status == Task.STATUS_TODO:
    #         msg = _('Started date cannot be set for not started tasks.')
    #         raise serializers.ValidationError(msg)
    #     if completed and status != Task.STATUS_DONE:
    #         msg = _('Completed date cannot be set for uncompleted tasks.')
    #         raise serializers.ValidationError(msg)
    #     return attrs

    def get_status_display(self,obj):
        return obj.get_status_display()    

    
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name',read_only = True)
    links = serializers.SerializerMethodField('get_links')

    class Meta:
        model = User
        fields = ('id',User.USERNAME_FIELD,'full_name','is_active','links')

    def get_links(self,obj):
        request = self.context['request']
        username = obj.get_username()
        return {
            'self':reverse('user-detail',
            kwargs={
                User.USERNAME_FIELD:obj.get_username()
            },
            request=request
            ),
            'tasks':'{}?assigned={}'.format(
                reverse('task-list',request=request),
                username
            )
        }

