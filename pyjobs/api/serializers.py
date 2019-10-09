import json
from datetime import datetime

from restless.serializers import JSONSerializer
from restless.utils import MoreTypesJSONEncoder

from pyjobs.core.models import Job
from django.contrib.auth.models import User


class PyJobsTypesJSONEncoder(MoreTypesJSONEncoder):
    """Overrides Restless's JSON encoder for custom format"""

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def default(self, data):
        if isinstance(data, datetime):
            return data.strftime(self.DATETIME_FORMAT)
        elif isinstance(data, User):
            return {
                "github": data.profile.github,
                "linkedin": data.profile.linkedin,
                "portfolio": data.profile.portfolio,
                "cellphone": data.profile.cellphone,
                "full_name": data.get_full_name(),
                "email": data.email,
            }
        elif isinstance(data, Job):
            return data.__str__()
        return super(PyJobsTypesJSONEncoder, self).default(data)


class PyJobsSerializer(JSONSerializer):
    """A version of restless's default serializer using PyJobsTypesJSONEncoder
    instead of the default restless.utils.MoreTypesJSONEncoder."""

    def serialize(self, data):
        return json.dumps(data, cls=PyJobsTypesJSONEncoder)
