from django.conf import settings


_DEFAULTS = {
    'EVENT_SCHEMA_VALIDATION': {
        'VALIDATOR': 'djangoevents.schema.LocalRepositoryValidator',
        'VALIDATOR_SCHEMA_DIR': 'avro',
    },
}

CONFIG = getattr(settings, 'EVENTSOURCING', _DEFAULTS)
