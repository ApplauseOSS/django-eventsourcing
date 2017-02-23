"""
Aggregate event avro schema validation
"""

import avro.schema
import os
import stringcase

from avro.io import Validate as avro_validate
from collections import defaultdict
from django.conf import settings
from .settings import CONFIG
from .domain import list_concrete_aggregates, list_aggregate_events
from .exceptions import EventSchemaError


schemas = defaultdict(dict)


def load_all_event_schemas():
    """
    Initializes aggregate event schemas lookup cache.
    """
    for aggregate in list_concrete_aggregates():
        for event in list_aggregate_events(aggregate_cls=aggregate):
            schemas[event] = load_event_schema(aggregate, event)

    return schemas


def load_event_schema(aggregate, event):
    spec_path = event_to_schema_path(aggregate, event)

    try:
        with open(spec_path) as fp:
            return load_event_schema(fp)
    except FileNotFoundError:
        msg = "No event schema found for: {event} (expecting file at:{path})."
        raise EventSchemaError(msg.format(event=event, path=spec_path))


def event_to_schema_path(aggregate_cls, event_cls):
    aggregate_name = decode_cls_name(aggregate_cls)
    event_name = decode_cls_name(event_cls)

    try:
        version = int(getattr(event_cls, 'schema_version', 1))
    except ValueError:
        msg = "`{}.schema_version` must be an integer. Currently it is {}"
        raise EventSchemaError(msg.format(event_cls, event_cls.sche))

    filename = "{aggregate_name}_{event_name}_{version}.json".format(
        aggregate_name=aggregate_name, event_name=event_name, version=version)

    avro_dir = CONFIG['EVENT_SCHEMA_VALIDATION']['VALIDATOR_SCHEMA_DIR']
    return os.path.join(settings.BASE_DIR, avro_dir, aggregate_name, filename)


def decode_cls_name(cls):
    """
    Convert camel case class name to snake case names used in event documentation.
    """
    return stringcase.snakecase(cls.__name__)


def load_event_schema(spec):
    schema = avro.schema.Parse(spec.read())
    return schema


def get_event_schema(event):
    return schemas[event]


def validate_event(event, schema=None):
    schema = schema or get_event_schema(event)
    return avro_validate(schema, event)
