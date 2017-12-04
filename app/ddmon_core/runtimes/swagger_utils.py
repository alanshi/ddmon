# coding=utf-8


"""
ref: https://gist.github.com/gjain0/f536d3988eb61e693ea306305c441bb7
"""


from __future__ import absolute_import, division, print_function, unicode_literals

import yaml
from yaml.error import YAMLError

from rest_framework import exceptions
from rest_framework.compat import coreapi, urlparse
from rest_framework.schemas import SchemaGenerator
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_swagger import renderers


class YAMLSchemaGenerator(SchemaGenerator):
    def get_link(self, path, method, view):
        """
        __doc__ in yaml format, eg:
        description: the desc of this api.
        parameters:
        - name: mobile
          description: the mobile number
          type: string
          required: true
          location: query
        - name: promotion
          description: the activity id
          type: int
          required: true
          location: form
        """
        method_desc = ''
        fields = self.get_path_fields(path, method, view)

        yaml_doc = None
        func = getattr(view, view.action) if getattr(view, 'action', None) else None
        if func and func.__doc__:
            try:
                index = func.__doc__.find('---\n')
                if index == -1:
                    raise YAMLError

                method_desc = func.__doc__[:index]

                yaml_str = func.__doc__[index:]
                yaml_doc = yaml.load(yaml_str)

            except YAMLError:
                pass

        if yaml_doc is None:
            return super(YAMLSchemaGenerator, self).get_link(path=path, method=method, view=view)

        if 'description' in yaml_doc:
            method_desc = yaml_doc.get('description', '')

        params = yaml_doc.get('parameters', [])
        for i in params:
            _name = i.get('name')
            _desc = i.get('description')
            _required = i.get('required', True)
            _type = i.get('type', 'string')
            _location = i.get('location', 'query')
            f = coreapi.Field(
                name=_name,
                location=_location,
                required=_required,
                description=_desc,
                type=_type
            )
            fields.append(f)

        fields += self.get_pagination_fields(path, method, view)
        fields += self.get_filter_fields(path, method, view)

        if fields and any([field.location in ('form', 'body') for field in fields]):
            encoding = self.get_encoding(path, method, view)
        else:
            encoding = None

        if self.url and path.startswith('/'):
            path = path[1:]

        return coreapi.Link(
            url=urlparse.urljoin(self.url, path),
            action=method.lower(),
            encoding=encoding,
            fields=fields,
            description=method_desc
        )


def get_swagger_view(title=None, url=None, patterns=None, urlconf=None):
    """
    Returns schema view which renders Swagger/OpenAPI.
    """
    class SwaggerSchemaView(APIView):
        _ignore_model_permissions = True
        exclude_from_schema = True
        permission_classes = [AllowAny]
        renderer_classes = [
            CoreJSONRenderer,
            renderers.OpenAPIRenderer,
            renderers.SwaggerUIRenderer
        ]

        @staticmethod
        def get(request):
            generator = YAMLSchemaGenerator(
                title=title,
                url=url,
                patterns=patterns,
                urlconf=urlconf
            )
            schema = generator.get_schema(request=request)

            if not schema:
                raise exceptions.ValidationError(
                    'The schema generator did not return a schema Document'
                )

            return Response(schema)

    return SwaggerSchemaView.as_view()
