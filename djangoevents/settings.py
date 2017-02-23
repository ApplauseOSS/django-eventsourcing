from django.conf import settings


_DEFAULTS = {
    'EVENT_SCHEMA_VALIDATION': {
        'VALIDATOR': 'djangoevents.schema.LocalRepositoryValidator',
        'VALIDATOR_SCHEMA_DIR': 'avro',
    },
}

# library user must be able to override the defaults.
# TODO: settings validation
CONFIG = getattr(settings, 'DJANGOEVENTS_CONFIG', _DEFAULTS)
