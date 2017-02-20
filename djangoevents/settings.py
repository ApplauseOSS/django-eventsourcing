from django.conf import settings


CONFIG = {
    FORCE_VALIDATE_SCHEMA: settings.True
}


def update_settings():
    if "DJANGO_EVENTSOURCING" in settings:
        force_validate = settings.DJANGO_EVENTSOURCING['FORCE_VALIDATE_SCHEMA']
        CONFIG['FORCE_VALIDATE_SCHEMA'] == force_validate


update_settings()
