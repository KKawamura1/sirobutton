from django import template


register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    """see: http://hideharaaws.hatenablog.com/entry/2015/01/16/002813"""
    get_params = request.GET.copy()
    get_params[field] = value
    return get_params.urlencode()
