from django.core.exceptions import ImproperlyConfigured
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response


class TemplateRenderer(TemplateHTMLRenderer):
    def _is_many(self, data):
        if not isinstance(data, dict):  # handle lists, ResultList, QuerySet, etc
            return True
        return False
    def get_template_names(self, response, view):
        try:
            return super().get_template_names(response, view)
        except ImproperlyConfigured:
            if self._is_many(response.data):
                return [f'{view.basename}_list.html']
            else:
                return [f'{view.basename}_detail.html']
    def get_template_context(self, *args, **kwargs):
        context = super().get_template_context(*args, **kwargs)
        if self._is_many(context):
            context = {"object_list": context}
        return context

class BrowserFacingMixin:  # mixes in to ModelViewSet
    renderer_classes = [JSONRenderer, TemplateRenderer]
    def get_renderer_context(self):
        base_context = super().get_renderer_context()
        base_context['view_name'] = self.get_view_name()
        return base_context
