from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.db.models import Model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django_lazyq.settings import MODELS_QUERY

import importlib

class LazyModelQueryAPI(View):

    def __init__(self, **kwargs):
        super(LazyModelQueryAPI, self).__init__(**kwargs)
        self.models_cls = self._lookup_all_models(MODELS_QUERY)

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        return HttpResponse("OK")

    def _lookup_all_models(self, models):
        models_classes = {}
        for model in models:
            rename, model_class_location = model
            if model_class_location is None:
                model_class_location = rename
            model_class = self._import_serializer_class(model_class_location)
            if not isinstance(model_class(), Model):
                raise TypeError('{0} is not instance of django model'.format(
                    model_class_location))
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
