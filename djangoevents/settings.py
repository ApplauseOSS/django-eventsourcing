from django.conf import settings


_DEFAULTS = {
    'EVENT_SCHEMA_VALIDATION': {
        'SCHEMA_DIR': 'avro',
    },
}

# library user must be able to override the defaults.
CONFIG = getattr(settings, 'DJANGOEVENTS_CONFIG', _DEFAULTS)


def schema_validation_enabled():
    return CONFIG.get('EVENT_SCHEMA_VALIDATION') is not None
