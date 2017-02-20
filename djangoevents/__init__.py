import warnings

from eventsourcing.domain.model.entity import DomainEvent
from eventsourcing.domain.model.entity import EventSourcedEntity
from eventsourcing.domain.model.entity import entity_mutator
from eventsourcing.domain.model.entity import singledispatch
from eventsourcing.domain.model.decorators import subscribe_to
from eventsourcing.domain.model.events import publish as es_publish
from eventsourcing.domain.model.events import subscribe
from eventsourcing.domain.model.events import unsubscribe
from eventsourcing.infrastructure.event_sourced_repo import EventSourcedRepository
from .domain import BaseEntity
from .app import EventSourcingWithDjango
from .settings import CONFIG

default_app_config = 'djangoevents.apps.AppConfig'

__all__ = [
    'DomainEvent',
    'EventSourcedEntity',
    'EventSourcedRepository',
    'entity_mutator',
    'singledispatch',
    'publish',
    'store_event'
    'subscribe',
    'unsubscribe',
    'subscribe_to',
    'BaseEntity',
    'EventSourcingWithDjango'
]


def publish(event):
    warnings.warn("`publish` is depreciated. Please switch to: `store_event`", DeprecationWarning)
    return es_publish(event)


def store_event(event, schema=None):
    """
    Store an event to the service's event journal. Optionally validates event
    schema if one is provided.
    """
    if CONFIG.FORCE_VALIDATE_SCHEMA and not schema:
        # TODO: Update to a specific exception
        raise Exception("Schema not provided for event: {}.".format(event))

    if CONFIG.FORCE_VALIDATE_SCHEMA and not hasattr(event, EVENT_SCHEMA_VERSION):
        # TODO: Update to a specific exception
        msg = "`EVENT_SCHEMA_VERSION` not set for event {}.".format(event)
        raise Exception(msg)

    if schema:
        validate_event(event, schema)

    return es_publish(event)


def validate_event(event, schema):
    """
    * https://github.com/datamountaineer/python-serializers
    * https://github.com/linkedin/python-avro-json-serializer
    """
    # TODO: Implement
