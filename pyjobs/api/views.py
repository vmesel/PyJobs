from django.core.paginator import Paginator
from restless.dj import DjangoResource
from restless.exceptions import BadRequest
from restless.preparers import FieldsPreparer

from pyjobs.api.serializers import PyJobsSerializer
from pyjobs.core.models import Job


class DjangoPaginatedResource(DjangoResource):
    """This will be unnecessary with next restless versions. For instante,
    see this recent (2019) progress for details:
    https://github.com/toastdriven/restless/issues/78"""

    def serialize_list(self, data):
        if data is None:
            return super(DjangoResource, self).serialize_list(data)

        paginator = Paginator(data, self.page_size)
        page_number = self.request.GET.get("page", 1)
        if page_number not in paginator.page_range:
            raise BadRequest("Invalid page number")

        self.page = paginator.page(page_number)
        data = self.page.object_list
        return super(DjangoResource, self).serialize_list(data)

    def wrap_list_response(self, data):
        response_dict = super(DjangoResource, self).wrap_list_response(data)

        if not hasattr(self, "page"):
            return response_dict

        next_page, previous_page = None, None
        if self.page.has_next() and self.page.next_page_number():
            next_page = True
        if self.page.has_previous() and self.page.previous_page_number():
            previous_page = True

        response_dict["meta"] = {
            "page": self.page.number,
            "limit": self.page.paginator.per_page,
            "total_pages": self.page.paginator.num_pages,
            "total_count": self.page.paginator.count,
            "next": next_page,
            "previous": previous_page,
        }
        return response_dict


class JobResource(DjangoPaginatedResource):
    page_size = 20
    serializer = PyJobsSerializer()
    preparer = FieldsPreparer(
        fields={
            field.name: field.name
            for field in Job._meta.fields
            if field.name not in {"premium", "public", "ad_interested", "company_email"}
        }
    )

    def list(self):
        return Job.objects.all()

    def detail(self, pk):
        return Job.objects.get(id=pk)
