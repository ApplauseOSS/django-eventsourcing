# from django.conf import settings

# This configuration should be overridable on the django.settings level
CONFIG = {
    'EVENT_SCHEMA_VALIDATION': {
        'VALIDATOR': 'djangoevents.schema.LocalRepositoryValidator',
        'VALIDATOR_SCHEMA_DIR': 'avro',
    },
}
