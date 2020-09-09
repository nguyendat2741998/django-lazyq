from django.conf import settings

MODELS_QUERY = getattr(settings, 'MODELS_QUERY', [])
