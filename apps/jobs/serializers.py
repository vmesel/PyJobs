from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        # when create a document get the currently autenticated user
        request = self.context['request']
        model = self.Meta.model
        return model.objects.create(empresa=request.user.company, **validated_data)

    class Meta:
        model = Job
        exclude = ['empresa']
