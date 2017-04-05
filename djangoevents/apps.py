from django.apps import AppConfig as BaseAppConfig
from django.conf import settings
from django.utils.module_loading import autodiscover_modules
from .exceptions import EventSchemaError
from .schema import load_all_event_schemas
import warnings


class AppConfig(BaseAppConfig):
    name = 'djangoevents'

    def ready(self):
        autodiscover_modules('handlers')
        autodiscover_modules('aggregates')

        # Once all handlers & aggregates are loaded we can import aggregate schema files.
        # `load_scheas()` assumes that all aggregates are imported at this point.
        load_schemas()


def get_app_module_names():
    return settings.INSTALLED_APPS


def load_schemas():
    """
    Try loading all the event schemas and complain loud if failure occurred.
    """
    try:
        load_all_event_schemas()
    except EventSchemaError as e:
        warnings.warn(str(e), UserWarning)
