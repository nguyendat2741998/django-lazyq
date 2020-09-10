from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.db.models import Model
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core import serializers
# from django.views.dec orators.http import
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django_lazyq.settings import MODELS_QUERY
from django_lazyq.forms import RequestFormValidate

import importlib
import json


@method_decorator(csrf_exempt, name='dispatch')
class LazyModelQueryAPI(View):

    def __init__(self, **kwargs):
        self.models_cls = self._lookup_all_models(MODELS_QUERY)
        super(LazyModelQueryAPI, self).__init__(**kwargs)

    def post(self, request):
        body_data = self._parse_request(request)
        request_data = self._validation(body_data)
        queryset = self._query_data(request_data)
        ser = serializers.serialize('json', queryset)
        return JsonResponse(ser.data)

    def _query_data(self, request_data):
        return ''

    def _validation(self, request_data):
        f = RequestFormValidate(data=request_data, models_cls=self.models_cls)
        if not f.is_valid():
            raise ValidationError(f.errors)
        return f.cleaned_data

    def _parse_request(self, request):
        body_unicode = request.body.decode('utf-8')
        return json.loads(body_unicode)

    def _lookup_all_models(self, models):
        models_classes = {}
        for model in models:
            rename, model_location = model
            if model_location is None:
                model_location = rename
            model_class = self._import_serializer_class(model_location)
            if not isinstance(model_class(), Model):
                raise TypeError('{0} is not instance of django model'.format(
                    model_location))
            models_classes[rename] = model_class
        return models_classes

    def _import_serializer_class(self, location: str):
        """
        Resolves a dot-notation string to serializer class.
        <app>.<SerializerName> will automatically be interpreted as:
        <app>.serializers.<SerializerName>
        """
        pieces = location.split(".")
        class_name = pieces.pop()

        if pieces[len(pieces) - 1] != "models":
            pieces.append("models")

        module = importlib.import_module(".".join(pieces))
        return getattr(module, class_name)
