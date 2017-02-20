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
from .schema import validate_event
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


def store_event(event):
    """
    Store an event to the service's event journal. Optionally validates event
    schema if one is provided.
    """
    if 'EVENT_SCHEMA_VALIDATION' in CONFIG:
        validate_event(event)

    return es_publish(event)
