from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def merge_query_params(context, **kwargs):
    query_params = context["request"].GET.copy()

    for k, v in kwargs.items():
        query_params[k] = v

    return query_params.urlencode()
