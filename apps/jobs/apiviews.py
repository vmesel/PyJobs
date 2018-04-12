from rest_framework import authentication, viewsets
from apps.core import authentication as core_authentication
from .serializers import JobSerializer
from .models import Job


class JobCreate(viewsets.ModelViewSet):
    authentication_classes = (authentication.SessionAuthentication, core_authentication.BearerTokenAuthentication)
    permission_classes = ()
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(empresa=self.request.user.company)
